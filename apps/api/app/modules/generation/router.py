import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.events import (
    GenerationCompletedEvent,
    GenerationStartedEvent,
    domain_event_bus,
)
from app.core.logging import logger
from app.db.models import User
from app.modules.ai.schemas import (
    ConvertFormatRequest,
    GenerateFromContentRequest,
    GenerateFromDataRequest,
    GenerateFromScratchRequest,
    GenerationResultResponse,
    RefineSectionRequest,
)
from app.modules.ai.service import ai_service
from app.modules.analysis.service import analysis_service
from app.modules.auth.deps import get_current_user

router = APIRouter(prefix="/generation", tags=["Paper Generation"])


@router.post("/generate", response_model=GenerationResultResponse)
async def generate_from_scratch(
    data: GenerateFromScratchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    event = GenerationStartedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        mode="from_scratch",
        paper_type=data.paper_type.value,
    )
    await domain_event_bus.publish(event)

    try:
        result = await ai_service.generate_from_scratch(data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    completion_event = GenerationCompletedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        version_id=result.job_id,
        title=result.title,
        mode="from_scratch",
    )
    await domain_event_bus.publish(completion_event)

    return result


@router.post("/from-content", response_model=GenerationResultResponse)
async def generate_from_content(
    data: GenerateFromContentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    event = GenerationStartedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        mode="from_content",
        paper_type=data.paper_type.value,
    )
    await domain_event_bus.publish(event)

    try:
        result = await ai_service.generate_from_content(data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Generation from content failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    completion_event = GenerationCompletedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        version_id=result.job_id,
        title=result.title,
        mode="from_content",
    )
    await domain_event_bus.publish(completion_event)

    return result


@router.post("/convert", response_model=GenerationResultResponse)
async def convert_format(
    data: ConvertFormatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    event = GenerationStartedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        mode="convert_format",
        paper_type=data.target_paper_type.value,
    )
    await domain_event_bus.publish(event)

    try:
        result = await ai_service.convert_format(data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Format conversion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

    completion_event = GenerationCompletedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        version_id=result.job_id,
        title=result.title,
        mode="convert_format",
    )
    await domain_event_bus.publish(completion_event)

    return result


@router.post("/refine")
async def refine_section(
    data: RefineSectionRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        refined_content = await ai_service.refine_section(data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Section refinement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

    return {
        "section_type": data.section_type.value,
        "refined_content": refined_content,
    }


@router.post("/from-data", response_model=GenerationResultResponse)
async def generate_from_data(
    data: GenerateFromDataRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    event = GenerationStartedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        mode="from_data",
        paper_type=data.paper_type.value,
    )
    await domain_event_bus.publish(event)

    try:
        from app.modules.analysis.schemas import AnalysisRequest, StatisticalTest

        analysis_result = await analysis_service.run_analysis(
            AnalysisRequest(
                project_id=data.project_id,
                data_id=data.data_id,
                research_question=data.research_question,
                variables=data.variables,
                tests=[StatisticalTest.DESCRIPTIVE, StatisticalTest.CORRELATION],
            ),
            data.data_id,
        )

        tables = await analysis_service.generate_paper_tables(
            data.data_id, data.research_question
        )
        figures = await analysis_service.generate_paper_figures(
            data.data_id, data.research_question
        )

        analysis_summary = analysis_result.summary
        tables_desc = "; ".join(
            [t.title + ": " + (t.caption or "") for t in tables]
        )
        figures_desc = "; ".join(
            [f.title + ": " + f.description for f in figures]
        )

        result = await ai_service.generate_from_data(
            data, analysis_summary, tables_desc, figures_desc
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Data-driven generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Generation failed: {str(e)}"
        )

    completion_event = GenerationCompletedEvent(
        event_id=str(uuid.uuid4()),
        project_id=data.project_id,
        version_id=result.job_id,
        title=result.title,
        mode="from_data",
    )
    await domain_event_bus.publish(completion_event)

    return result


@router.get("/health")
async def generation_health():
    from app.modules.ai.client import gemini_client

    return {
        "status": "available" if gemini_client.is_available else "unavailable",
        "model": "gemini-2.0-flash" if gemini_client.is_available else None,
    }


@router.get("/dashboard")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
):
    """Quick stats for dashboard — counts from local state."""
    import os

    from app.modules.ai.client import gemini_client
    from app.modules.plugins.v1.registry import list_plugins

    storage_dir = settings.ORIGINAL_INPUTS_DIR
    file_count = 0
    file_types: dict[str, int] = {}
    if os.path.exists(storage_dir):
        for f in os.listdir(storage_dir):
            fp = os.path.join(storage_dir, f)
            if os.path.isfile(fp):
                file_count += 1
                ext = os.path.splitext(f)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1

    export_dir = "exports"
    export_count = 0
    export_types: dict[str, int] = {}
    if os.path.exists(export_dir):
        for f in os.listdir(export_dir):
            fp = os.path.join(export_dir, f)
            if os.path.isfile(fp):
                export_count += 1
                ext = os.path.splitext(f)[1].lower()
                export_types[ext] = export_types.get(ext, 0) + 1

    storage_size = 0
    if os.path.exists(storage_dir):
        for f in os.listdir(storage_dir):
            fp = os.path.join(storage_dir, f)
            if os.path.isfile(fp):
                storage_size += os.path.getsize(fp)

    plugins = list_plugins()

    return {
        "total_files": file_count,
        "total_exports": export_count,
        "total_publishers": len(plugins),
        "file_types": file_types,
        "export_types": export_types,
        "storage_size_bytes": storage_size,
        "gemini_status": (
            "available" if gemini_client.is_available else "unavailable"
        ),
        "dev_mode": settings.DEV_MODE,
    }


@router.get("/search")
async def search_files(
    q: str = "",
    current_user: User = Depends(get_current_user),
):
    """Search uploaded files by name."""
    import os

    storage_dir = settings.ORIGINAL_INPUTS_DIR
    results = []
    if os.path.exists(storage_dir) and q:
        for f in os.listdir(storage_dir):
            if q.lower() in f.lower():
                fp = os.path.join(storage_dir, f)
                results.append({
                    "filename": f,
                    "size": os.path.getsize(fp),
                    "type": os.path.splitext(f)[1].lower(),
                })

    export_dir = "exports"
    if os.path.exists(export_dir) and q:
        for f in os.listdir(export_dir):
            if q.lower() in f.lower():
                fp = os.path.join(export_dir, f)
                results.append({
                    "filename": f,
                    "size": os.path.getsize(fp),
                    "type": os.path.splitext(f)[1].lower(),
                    "is_export": True,
                })

    return {"query": q, "results": results[:20], "total": len(results)}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a document for analysis and content extraction."""
    allowed = {".pdf", ".docx", ".doc", ".tex", ".latex", ".md", ".txt", ".csv", ".json"}
    ext = os.path.splitext(file.filename or "")[1].lower()

    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    os.makedirs(settings.ORIGINAL_INPUTS_DIR, exist_ok=True)
    save_path = os.path.join(settings.ORIGINAL_INPUTS_DIR, safe_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    file_id = f"file-{uuid.uuid4().hex[:12]}"
    file_size = len(content)

    text_content = ""
    if ext in {".txt", ".md", ".csv", ".json"}:
        text_content = content.decode("utf-8", errors="ignore")

    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": file_size,
        "type": ext.lstrip("."),
        "status": "uploaded",
        "preview": (
            text_content[:2000]
            if text_content
            else f"Binary file ({ext}) uploaded. Parse to extract content."
        ),
    }


@router.post("/analyze-text")
async def analyze_text(
    text: str = "",
    current_user: User = Depends(get_current_user),
):
    """Quick NLP analysis without DB — returns stats, entities, keywords."""
    import re
    from collections import Counter

    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_count = len(words)
    sentence_count = len(sentences)
    avg_sentence_length = round(word_count / max(sentence_count, 1), 1)
    unique_words = len(set(words))
    lexical_diversity = round(unique_words / max(word_count, 1), 3)

    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "can", "this", "that", "these",
        "those", "it", "its", "not", "no", "if", "then", "than", "so",
    }
    content_words = [w for w in words if w not in stopwords and len(w) > 2]
    keywords = [w for w, _ in Counter(content_words).most_common(15)]

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)

    doi_pattern = r"(?:doi[:\s]*|10\.\d{4,}/)[^\s]+"
    dois = re.findall(doi_pattern, text)

    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)

    org_keywords = ["university", "institute", "lab", "center", "department", "school"]
    sentences_with_orgs = [s for s in sentences if any(kw in s.lower() for kw in org_keywords)]
    orgs = [s.split(",")[0].strip() for s in sentences_with_orgs[:5]]

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "lexical_diversity": lexical_diversity,
        "unique_words": unique_words,
        "reading_time_mins": round(word_count / 200, 1),
        "keywords": keywords,
        "entities": (
            [{"text": e, "type": "EMAIL"} for e in emails[:5]]
            + [{"text": d, "type": "DOI"} for d in dois[:5]]
            + [{"text": u, "type": "URL"} for u in urls[:5]]
            + [{"text": o, "type": "ORGANIZATION"} for o in orgs]
        ),
    }


@router.post("/generate/stream")
async def generate_stream(
    data: GenerateFromScratchRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream generated paper sections as Server-Sent Events."""
    from app.modules.ai.client import gemini_client
    from app.modules.ai.prompts import (
        get_keywords_generation_prompt,
        get_section_generation_prompt,
        get_system_instruction,
        get_title_generation_prompt,
    )

    if not gemini_client.is_available:
        raise HTTPException(status_code=503, detail="Gemini API not configured.")

    async def event_generator():
        section_order = [
            "abstract", "introduction", "methodology",
            "results", "discussion", "conclusion",
        ]

        yield f"data: {json.dumps({'type': 'started', 'message': 'Generation started'})}\n\n"

        try:
            system_inst = get_system_instruction(data.paper_type)

            yield f"data: {json.dumps({'type': 'step', 'message': 'Generating title'})}\n\n"
            title_resp = await gemini_client.generate(
                get_title_generation_prompt(
                    data.topic, data.keywords, data.paper_type, data.research_domain
                ),
                system_instruction=system_inst,
            )
            titles = [t.strip() for t in title_resp.strip().split("\n") if t.strip()]
            title = titles[0] if titles else data.topic
            yield f"data: {json.dumps({'type': 'title', 'title': title})}\n\n"

            yield f"data: {json.dumps({'type': 'step', 'message': 'Generating keywords'})}\n\n"
            keywords_resp = await gemini_client.generate(
                get_keywords_generation_prompt(
                    title, "", data.research_domain
                ),
                system_instruction=system_inst,
            )
            keywords = [k.strip() for k in keywords_resp.strip().split(",") if k.strip()]

            yield f"data: {json.dumps({'type': 'keywords', 'keywords': keywords})}\n\n"

            abstract_resp = await gemini_client.generate(
                get_section_generation_prompt(
                    section_type="abstract",
                    title=title,
                    topic=data.topic,
                    paper_type=data.paper_type,
                    abstract="",
                ),
                system_instruction=system_inst,
            )
            abstract_event = {
                "type": "section",
                "name": "abstract",
                "content": abstract_resp.strip(),
            }
            yield f"data: {json.dumps(abstract_event)}\n\n"

            collected = {}
            for section in section_order[1:]:
                step_msg = f"Generating {section}"
                yield f"data: {json.dumps({'type': 'step', 'message': step_msg})}\n\n"
                resp = await gemini_client.generate(
                    get_section_generation_prompt(
                        section_type=section,
                        title=title,
                        topic=data.topic,
                        paper_type=data.paper_type,
                        abstract="",
                    ),
                    system_instruction=system_inst,
                )
                content = resp.strip()
                collected[section] = content
                sec_event = {"type": "section", "name": section, "content": content}
                yield f"data: {json.dumps(sec_event)}\n\n"

            complete_event = {
                "type": "complete",
                "title": title,
                "keywords": keywords,
                "sections": list(collected.keys()),
            }
            yield f"data: {json.dumps(complete_event)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
