import datetime
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel


class DomainProcessRequest(BaseModel):
    project_id: uuid.UUID
    version_id: uuid.UUID


class DomainProcessResponse(BaseModel):
    job_id: uuid.UUID
    detail: str


class DomainJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_id: uuid.UUID
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class DomainDocResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_id: uuid.UUID
    primary_domain: str
    primary_domain_confidence: float
    subdomain: str
    subdomain_confidence: float
    research_type: str
    research_type_confidence: float
    publication_type: str
    publication_type_confidence: float
    citation_style: str
    citation_style_confidence: float
    processed_at: datetime.datetime

    model_config = {"from_attributes": True}


class DomainTerminologyResponse(BaseModel):
    id: uuid.UUID
    term: str
    frequency: int
    term_type: str

    model_config = {"from_attributes": True}


class DomainStructureResponse(BaseModel):
    id: uuid.UUID
    expected_sections: Dict[str, Any]
    missing_sections: Dict[str, Any]
    extra_sections: Dict[str, Any]
    is_order_correct: bool

    model_config = {"from_attributes": True}
