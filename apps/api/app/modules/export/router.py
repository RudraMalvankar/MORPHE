from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.export.repository import ExportArtifactRepository
from app.modules.export.schemas import ExportFormat, ExportJobResponse, ExportRequest
from app.modules.export.service import ExportService
from app.modules.plugins.v1.registry import list_plugins

router = APIRouter(prefix="/export", tags=["Export Engine"])


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    repo = ExportArtifactRepository(db)
    return ExportService(artifact_repo=repo)


@router.get("/formats", response_model=List[Dict[str, str]])
async def list_export_formats():
    return [
        {"format": "pdf", "name": "PDF (Typst)", "description": "Professional PDF"},
        {"format": "latex", "name": "LaTeX", "description": "LaTeX source"},
        {"format": "docx", "name": "Word", "description": "Microsoft Word"},
        {"format": "html", "name": "HTML", "description": "Web HTML"},
    ]


@router.get("/publishers")
async def list_publishers():
    return list_plugins()


@router.get("/publishers/{publisher_key}")
async def get_publisher(publisher_key: str):
    plugins = list_plugins()
    for p in plugins:
        if p["key"] == publisher_key:
            return p
    raise HTTPException(status_code=404, detail=f"Publisher '{publisher_key}' not found")


@router.post("/generate", response_model=ExportJobResponse)
async def export_paper(
    request: ExportRequest,
    service: ExportService = Depends(get_export_service),
):
    cdm = {
        "title": "Research Paper",
        "authors": ["Author"],
        "abstract": "",
        "sections": [],
        "references": [],
        "keywords": [],
    }
    return await service.export_paper(request, cdm)


@router.post("/preview")
async def preview_export(
    publisher_key: str = "ieee",
    format: ExportFormat = ExportFormat.HTML,
    cdm: Dict[str, Any] = {},
):
    from app.modules.plugins.v1.registry import get_plugin

    plugin = get_plugin(publisher_key)
    service = ExportService(artifact_repo=None)

    if format == ExportFormat.HTML:
        return {"html": service._render_html(cdm, plugin)}
    elif format == ExportFormat.LATEX:
        return {"latex": service._render_latex(cdm, plugin)}
    elif format == ExportFormat.DOCX:
        return {"docx_xml": service._render_docx_xml(cdm, plugin)}
    else:
        return {"typst": service._render_typst(cdm, plugin)}
