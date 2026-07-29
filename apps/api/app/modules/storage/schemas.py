import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


class StorageObjectResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_id: Optional[uuid.UUID]
    owner_id: uuid.UUID
    original_filename: str
    storage_filename: str
    checksum: str
    file_size: int
    mime_type: str
    storage_provider: str
    storage_path: str
    status: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class StorageRestoreResponse(BaseModel):
    detail: str
    file_id: uuid.UUID
    version_id: uuid.UUID


class VersionFilesResponse(BaseModel):
    version_id: uuid.UUID
    version_number: int
    commit_message: str
    created_at: datetime.datetime
    files: List[StorageObjectResponse]
