from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.modules.knowledge.schemas import (
    CitationEntry,
    KBSearchRequest,
    KBSearchResponse,
)
from app.modules.knowledge.service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

kb_service = KnowledgeBaseService()


@router.get("/publishers", response_model=Dict[str, Any])
async def list_publisher_guidelines():
    return await kb_service.list_all_guidelines()


@router.get("/publishers/{publisher_key}", response_model=Dict[str, Any])
async def get_publisher_guideline(publisher_key: str):
    result = await kb_service.get_publisher_guidelines(publisher_key)
    if not result:
        raise HTTPException(status_code=404, detail=f"Publisher '{publisher_key}' not found")
    return result


@router.get("/citations", response_model=Dict[str, Any])
async def list_citation_styles():
    return await kb_service.list_citation_styles()


@router.get("/citations/{style_key}", response_model=Dict[str, Any])
async def get_citation_style(style_key: str):
    result = await kb_service.get_citation_style(style_key)
    if not result:
        raise HTTPException(status_code=404, detail=f"Citation style '{style_key}' not found")
    return result


@router.post("/citations/format")
async def format_citation(citation: CitationEntry, style: str = "apa", index: int = 1):
    formatted = await kb_service.format_citation(citation, style, index)
    return {"formatted": formatted, "style": style}


@router.get("/journals", response_model=List[Dict[str, Any]])
async def list_journals(publisher_key: Optional[str] = Query(None)):
    return await kb_service.list_journals(publisher_key)


@router.get("/journals/{journal_key}", response_model=Dict[str, Any])
async def get_journal_metrics(journal_key: str):
    result = await kb_service.get_journal_metrics(journal_key)
    if not result:
        raise HTTPException(status_code=404, detail=f"Journal '{journal_key}' not found")
    return result


@router.post("/search", response_model=KBSearchResponse)
async def search_knowledge_base(request: KBSearchRequest):
    return await kb_service.search(request)


@router.get("/stats")
async def kb_stats():
    guidelines = await kb_service.list_all_guidelines()
    styles = await kb_service.list_citation_styles()
    journals = await kb_service.list_journals()
    return {
        "publishers": len(guidelines),
        "citation_styles": len(styles),
        "journals": len(journals),
    }
