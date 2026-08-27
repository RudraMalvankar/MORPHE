from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class KBCategory(str, Enum):
    PUBLISHER_GUIDELINES = "publisher_guidelines"
    CITATION_STYLES = "citation_styles"
    JOURNAL_METRICS = "journal_metrics"
    FIELD_CONVENTIONS = "field_conventions"
    TEMPLATE_DATA = "template_data"


class PublisherGuidelines(BaseModel):
    publisher_key: str
    name: str
    manuscript_types: List[str] = Field(default_factory=list)
    word_limit: Optional[int] = None
    page_limit: Optional[int] = None
    reference_limit: Optional[int] = None
    figure_limit: Optional[int] = None
    table_limit: Optional[int] = None
    abstract_word_limit: Optional[int] = None
    abstract_structure: List[str] = Field(default_factory=list)
    required_sections: List[str] = Field(default_factory=list)
    optional_sections: List[str] = Field(default_factory=list)
    file_formats: List[str] = Field(default_factory=list)
    figure_dpi: Optional[int] = None
    color_online: bool = False
    supplementary_materials: bool = False
    open_access: bool = False
    submission_url: Optional[str] = None
    review_process: Optional[str] = None
    publication_fee: Optional[str] = None
    acceptance_rate: Optional[float] = None
    turnaround_weeks: Optional[int] = None


class CitationEntry(BaseModel):
    id: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    title: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    year: str = ""
    doi: str = ""
    publisher_key: str = ""
    citation_style: str = ""
    formatted_citation: str = ""


class JournalMetrics(BaseModel):
    publisher_key: str
    journal_name: str
    impact_factor: Optional[float] = None
    h_index: Optional[int] = None
    quartile: Optional[str] = None
    cite_score: Optional[float] = None
    sjr: Optional[float] = None
    snip: Optional[float] = None
    apc: Optional[str] = None
    review_cycle_weeks: Optional[int] = None
    acceptance_rate: Optional[float] = None
    topics: List[str] = Field(default_factory=list)


class FieldConvention(BaseModel):
    field: str
    terminology: Dict[str, str] = Field(default_factory=dict)
    abbreviations: Dict[str, str] = Field(default_factory=dict)
    units: Dict[str, str] = Field(default_factory=dict)
    formatting_rules: Dict[str, str] = Field(default_factory=dict)


class TemplateData(BaseModel):
    template_key: str
    publisher_key: str
    paper_type: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    sample_content: Dict[str, str] = Field(default_factory=dict)


class KBEntryResponse(BaseModel):
    id: str
    category: str
    key: str
    value: Any


class KBSearchRequest(BaseModel):
    category: Optional[KBCategory] = None
    query: str = ""
    publisher_key: Optional[str] = None
    limit: int = 50


class KBSearchResponse(BaseModel):
    results: List[KBEntryResponse]
    total: int
    query: str
