import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SectionType(str, Enum):
    TITLE = "title"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    FUTURE_WORK = "future_work"
    CASE_PRESENTATION = "case_presentation"
    STATUTES = "statutes"
    REFERENCES = "references"
    APPENDIX = "appendix"
    ACKNOWLEDGEMENTS = "acknowledgements"
    CUSTOM = "custom"


class Author(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    orcid: Optional[str] = None
    affiliations: List[str] = Field(default_factory=list)
    is_corresponding: bool = False


class CitationRef(BaseModel):
    id: str
    raw_text: str
    authors: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    journal_or_book: Optional[str] = None
    year: Optional[int] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None


class MediaObject(BaseModel):
    id: str
    caption: str
    type: str  # "figure" | "table" | "code_snippet" | "formula"
    url_or_path: Optional[str] = None
    raw_content: Optional[str] = None


class DocumentSection(BaseModel):
    id: str
    section_type: SectionType
    title: str
    content_markdown: str
    order: int
    subsections: List["DocumentSection"] = Field(default_factory=list)
    media_ids: List[str] = Field(default_factory=list)


class CanonicalDocument(BaseModel):
    id: str
    version_id: str
    domain_profile_id: str = "general"
    title: str
    subtitle: Optional[str] = None
    authors: List[Author] = Field(default_factory=list)
    abstract: str
    keywords: List[str] = Field(default_factory=list)
    sections: List[DocumentSection] = Field(default_factory=list)
    references: List[CitationRef] = Field(default_factory=list)
    media_objects: List[MediaObject] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


DocumentSection.model_rebuild()
