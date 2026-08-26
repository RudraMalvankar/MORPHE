from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PaperType(str, Enum):
    RESEARCH_ARTICLE = "research_article"
    REVIEW_ARTICLE = "review_article"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_STUDY = "case_study"
    POSITION_PAPER = "position_paper"
    CONFERENCE_PAPER = "conference_paper"
    THEORETICAL_PAPER = "theoretical_paper"
    METHODOLOGICAL_PAPER = "methodological_paper"
    LITERATURE_REVIEW = "literature_review"
    TECHNICAL_REPORT = "technical_report"
    THESIS = "thesis"
    WHITE_PAPER = "white_paper"


class GenerationMode(str, Enum):
    FROM_SCRATCH = "from_scratch"
    FROM_CONTENT = "from_content"
    FROM_UPLOAD = "from_upload"
    FROM_DATA = "from_data"
    CONVERT_FORMAT = "convert_format"


class CitationStyle(str, Enum):
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"
    AMA = "ama"
    ACS = "acs"
    TURABIAN = "turabian"


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
    ACKNOWLEDGEMENTS = "acknowledgements"
    REFERENCES = "references"


class GenerateFromScratchRequest(BaseModel):
    project_id: str
    topic: str
    keywords: List[str] = Field(default_factory=list)
    paper_type: PaperType = PaperType.RESEARCH_ARTICLE
    citation_style: CitationStyle = CitationStyle.IEEE
    target_publisher: str = "ieee"
    research_domain: str = "general"
    research_subdomain: Optional[str] = None
    methodology_type: Optional[str] = None
    additional_instructions: Optional[str] = None
    language: str = "en"


class GenerateFromContentRequest(BaseModel):
    project_id: str
    raw_content: str
    paper_type: PaperType = PaperType.RESEARCH_ARTICLE
    citation_style: CitationStyle = CitationStyle.IEEE
    target_publisher: str = "ieee"
    additional_instructions: Optional[str] = None
    language: str = "en"


class ConvertFormatRequest(BaseModel):
    project_id: str
    source_content: str
    target_paper_type: PaperType = PaperType.RESEARCH_ARTICLE
    target_publisher: str = "ieee"
    target_citation_style: CitationStyle = CitationStyle.IEEE
    additional_instructions: Optional[str] = None


class RefineSectionRequest(BaseModel):
    project_id: str
    version_id: str
    section_type: SectionType
    current_content: str
    feedback: str


class GeneratedSection(BaseModel):
    section_type: SectionType
    title: str
    content: str
    order: int


class GenerationJobResponse(BaseModel):
    job_id: str
    status: str
    project_id: str
    mode: GenerationMode
    message: str


class GenerationResultResponse(BaseModel):
    job_id: str
    status: str
    title: str
    abstract: str
    sections: List[GeneratedSection]
    keywords: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
