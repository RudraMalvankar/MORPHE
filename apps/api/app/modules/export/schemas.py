from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    PDF = "pdf"
    LATEX = "latex"
    DOCX = "docx"
    HTML = "html"


class ExportRequest(BaseModel):
    version_id: str
    project_id: str
    format: ExportFormat = ExportFormat.PDF
    publisher_key: str = "ieee"


class ExportJobResponse(BaseModel):
    job_id: str
    status: str
    format: str
    publisher: str
    message: str


class ExportArtifactResponse(BaseModel):
    id: str
    version_id: str
    publisher_key: str
    export_type: str
    file_path: str
    created_at: Any


class CitationStyleConfig(BaseModel):
    in_text_format: str
    reference_format: str
    order: str = "numbered"
    separator: str = ", "


class LayoutRules(BaseModel):
    page_size: str = "a4"
    columns: int = 2
    column_gap: str = "0.25in"
    margins: Dict[str, str] = Field(
        default_factory=lambda: {
            "top": "0.75in",
            "bottom": "1in",
            "left": "0.625in",
            "right": "0.625in",
        }
    )
    font_family: str = "Times New Roman"
    font_size: str = "10pt"
    title_font_size: str = "24pt"
    heading_font_size: str = "12pt"
    line_spacing: float = 1.0
    abstract_font_size: str = "9pt"
    references_font_size: str = "8pt"


class PublisherPluginInfo(BaseModel):
    key: str
    name: str
    latex_class: str
    citation_style: str
    columns: int
    page_size: str
