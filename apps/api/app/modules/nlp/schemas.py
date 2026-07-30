import datetime
import uuid
from typing import Optional

from pydantic import BaseModel


class NlpProcessRequest(BaseModel):
    project_id: uuid.UUID
    version_id: uuid.UUID


class NlpProcessResponse(BaseModel):
    job_id: uuid.UUID
    detail: str


class NlpJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_id: uuid.UUID
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class NlpEntityResponse(BaseModel):
    id: uuid.UUID
    entity_text: str
    entity_type: str
    confidence: float

    model_config = {"from_attributes": True}


class NlpKeywordResponse(BaseModel):
    id: uuid.UUID
    keyword: str
    score: float

    model_config = {"from_attributes": True}


class NlpStatisticsResponse(BaseModel):
    id: uuid.UUID
    word_count: int
    sentence_count: int
    paragraph_count: int
    section_count: int
    avg_sentence_length: float
    lexical_diversity: float
    vocabulary_size: int
    reading_time_mins: float

    model_config = {"from_attributes": True}


class NlpLanguageResponse(BaseModel):
    language: str
    confidence: float
