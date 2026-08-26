from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    default_publisher_target: str = Field("ieee", max_length=100)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    default_publisher_target: Optional[str] = Field(None, max_length=100)


class PaperVersionResponse(BaseModel):
    id: str
    version_number: int
    commit_message: str
    detected_domain: Optional[str] = None
    detected_subdomain: Optional[str] = None
    detected_research_type: Optional[str] = None
    detected_publication_type: Optional[str] = None
    detected_citation_style: Optional[str] = None
    readiness_rating: Optional[int] = None
    quality_score: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    default_publisher_target: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(ProjectResponse):
    versions: List[PaperVersionResponse] = Field(default_factory=list)


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
