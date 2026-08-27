import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

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
