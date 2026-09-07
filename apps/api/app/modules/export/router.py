from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.export.repository import ExportArtifactRepository
from app.modules.export.schemas import ExportFormat, ExportJobResponse, ExportRequest
from app.modules.export.service import ExportService
from app.modules.plugins.v1.registry import list_plugins

router = APIRouter(prefix="/export", tags=["Export Engine"])


def _build_cdm(request: ExportRequest) -> Dict[str, Any]:
    data = request.cdm_data or {}
    return {
        "title": data.get("title", "Research Paper"),
        "authors": data.get("authors", ["Author"]),
        "abstract": data.get("abstract", ""),
        "sections": data.get("sections", []),
        "references": data.get("references", []),
        "keywords": data.get("keywords", []),
    }


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
    cdm = _build_cdm(request)
    return await service.export_paper(request, cdm)


@router.post("/download")
async def download_export(
    request: ExportRequest,
    service: ExportService = Depends(get_export_service),
):
    cdm = _build_cdm(request)
    result = await service.export_paper(request, cdm)

    import os
    ext_map = {"pdf": ".pdf", "latex": ".tex", "docx": ".docx", "html": ".html"}
    ext = ext_map.get(request.format.value, ".txt")
    file_path = service.export_dir / f"{result.job_id}{ext}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Export file not generated")

    media_types = {
        "pdf": "application/pdf",
        "latex": "application/x-tex",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "html": "text/html",
    }

    return FileResponse(
        path=str(file_path),
        media_type=media_types.get(request.format.value, "application/octet-stream"),
        filename=f"paper_{request.publisher_key}_{request.format.value}{ext}",
    )


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
