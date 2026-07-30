import uuid
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_dependency
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.modules.auth.deps import get_current_user
from app.modules.nlp.repository import (
    NlpDocumentRepository,
    NlpEntityRepository,
    NlpJobRepository,
    NlpKeywordRepository,
    NlpStatisticsRepository,
)
from app.modules.nlp.schemas import (
    NlpEntityResponse,
    NlpJobResponse,
    NlpKeywordResponse,
    NlpLanguageResponse,
    NlpProcessRequest,
    NlpProcessResponse,
    NlpStatisticsResponse,
)
from app.modules.nlp.service import NlpService
from app.modules.projects.repository import ProjectRepository


def get_session_maker() -> Any:

    return AsyncSessionLocal


router = APIRouter()


@router.post(
    "/nlp/process", response_model=NlpProcessResponse, status_code=status.HTTP_202_ACCEPTED
)
async def process_nlp(
    background_tasks: BackgroundTasks,
    request_data: NlpProcessRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
    session_maker: Any = Depends(get_session_maker),
):
    proj_repo = ProjectRepository(db)
    proj = await proj_repo.get_by_id(request_data.project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if proj.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    job = await NlpService.create_job(db, request_data.project_id, request_data.version_id)

    background_tasks.add_task(NlpService.run_nlp_pipeline, session_maker, job.id)

    return NlpProcessResponse(job_id=job.id, detail="NLP processing task successfully queued")


@router.get("/nlp/jobs/{job_id}", response_model=NlpJobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job_repo = NlpJobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="NLP job not found")

    return job


@router.get("/nlp/results/{job_id}")
async def get_job_results(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job_repo = NlpJobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="NLP job not found")

    if job.status != "completed":
        return {
            "status": job.status,
            "progress": job.progress,
            "error_message": job.error_message,
            "detail": "NLP job is not completed yet.",
        }

    nlp_doc_repo = NlpDocumentRepository(db)
    nlp_doc = await nlp_doc_repo.get_by_version(job.version_id)
    if not nlp_doc:
        raise HTTPException(status_code=404, detail="NLP Document output artifact missing")

    return {
        "status": "completed",
        "job_id": job_id,
        "document_id": nlp_doc.id,
        "language": nlp_doc.language,
    }


@router.get("/nlp/entities/{document_id}", response_model=List[NlpEntityResponse])
async def get_nlp_entities(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    # Try looking up by document ID first, fallback to paper version ID
    nlp_doc_repo = NlpDocumentRepository(db)
    doc_obj = await nlp_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await nlp_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="NLP Document not found")

    entity_repo = NlpEntityRepository(db)
    entities = await entity_repo.list_by_document(doc_obj.id)
    return entities


@router.get("/nlp/keywords/{document_id}", response_model=List[NlpKeywordResponse])
async def get_nlp_keywords(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    nlp_doc_repo = NlpDocumentRepository(db)
    doc_obj = await nlp_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await nlp_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="NLP Document not found")

    kw_repo = NlpKeywordRepository(db)
    keywords = await kw_repo.list_by_document(doc_obj.id)
    return keywords


@router.get("/nlp/statistics/{document_id}", response_model=NlpStatisticsResponse)
async def get_nlp_statistics(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    nlp_doc_repo = NlpDocumentRepository(db)
    doc_obj = await nlp_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await nlp_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="NLP Document not found")

    stats_repo = NlpStatisticsRepository(db)
    stats = await stats_repo.get_by_document(doc_obj.id)
    if not stats:
        raise HTTPException(status_code=404, detail="Statistics not found for this document")
    return stats


@router.get("/nlp/language/{document_id}", response_model=NlpLanguageResponse)
async def get_nlp_language(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    nlp_doc_repo = NlpDocumentRepository(db)
    doc_obj = await nlp_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await nlp_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="NLP Document not found")

    return NlpLanguageResponse(language=doc_obj.language, confidence=doc_obj.language_confidence)
