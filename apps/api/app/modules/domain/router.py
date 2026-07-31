import uuid
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_dependency
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.modules.auth.deps import get_current_user
from app.modules.domain.repository import (
    DomainDocRepository,
    DomainJobRepository,
    DomainStructureAnalysisRepository,
    DomainTerminologyRepository,
)
from app.modules.domain.schemas import (
    DomainDocResponse,
    DomainJobResponse,
    DomainProcessRequest,
    DomainProcessResponse,
    DomainStructureResponse,
    DomainTerminologyResponse,
)
from app.modules.domain.service import DomainService
from app.modules.projects.repository import ProjectRepository


def get_session_maker() -> Any:

    return AsyncSessionLocal


router = APIRouter()


@router.post(
    "/domain/process", response_model=DomainProcessResponse, status_code=status.HTTP_202_ACCEPTED
)
async def process_domain(
    background_tasks: BackgroundTasks,
    request_data: DomainProcessRequest,
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

    job = await DomainService.create_job(db, request_data.project_id, request_data.version_id)

    background_tasks.add_task(DomainService.run_domain_pipeline, session_maker, job.id)

    return DomainProcessResponse(
        job_id=job.id, detail="Domain intelligence processing task successfully queued"
    )


@router.get("/domain/jobs/{job_id}", response_model=DomainJobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job_repo = DomainJobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Domain job not found")

    return job


@router.get("/domain/results/{job_id}")
async def get_job_results(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job_repo = DomainJobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Domain job not found")

    if job.status != "completed":
        return {
            "status": job.status,
            "progress": job.progress,
            "error_message": job.error_message,
            "detail": "Domain analysis is not completed yet.",
        }

    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_version(job.version_id)
    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain output document missing")

    return {
        "status": "completed",
        "job_id": job_id,
        "document_id": doc_obj.id,
        "primary_domain": doc_obj.primary_domain,
    }


@router.get("/domain/{document_id}", response_model=DomainDocResponse)
async def get_domain_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await domain_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain document record not found")

    return doc_obj


@router.get("/domain/terminology/{document_id}", response_model=List[DomainTerminologyResponse])
async def get_domain_terminology(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await domain_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain document record not found")

    term_repo = DomainTerminologyRepository(db)
    terms = await term_repo.list_by_document(doc_obj.id)
    return terms


@router.get("/domain/structure/{document_id}", response_model=DomainStructureResponse)
async def get_domain_structure(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await domain_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain document record not found")

    struct_repo = DomainStructureAnalysisRepository(db)
    struct = await struct_repo.get_by_document(doc_obj.id)
    if not struct:
        raise HTTPException(status_code=404, detail="Structural analysis records missing")
    return struct


@router.get("/domain/research-type/{document_id}")
async def get_domain_research_type(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await domain_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain document record not found")

    return {
        "document_id": doc_obj.id,
        "research_type": doc_obj.research_type,
        "confidence": doc_obj.research_type_confidence,
    }


@router.get("/domain/publication-type/{document_id}")
async def get_domain_publication_type(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    domain_doc_repo = DomainDocRepository(db)
    doc_obj = await domain_doc_repo.get_by_id(document_id)
    if not doc_obj:
        doc_obj = await domain_doc_repo.get_by_version(document_id)

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Domain document record not found")

    return {
        "document_id": doc_obj.id,
        "publication_type": doc_obj.publication_type,
        "confidence": doc_obj.publication_type_confidence,
    }
