import datetime
import uuid
from typing import Optional

from pydantic import BaseModel


class IngestionJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_id: Optional[uuid.UUID]
    file_id: uuid.UUID
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class IngestionUploadResponse(BaseModel):
    job_id: uuid.UUID
    detail: str


class IngestionParseRequest(BaseModel):
    project_id: uuid.UUID
    version_id: Optional[uuid.UUID] = None
    file_id: uuid.UUID
