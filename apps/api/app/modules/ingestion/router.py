import uuid
from typing import Any, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_dependency
from app.db.models import User
from app.db.session import AsyncSessionLocal  # session maker for background task execution
from app.modules.auth.deps import get_current_user
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.cdm.schemas import CanonicalDocument
from app.modules.ingestion.schemas import (
    IngestionJobResponse,
    IngestionParseRequest,
    IngestionUploadResponse,
)
from app.modules.ingestion.service import IngestionService
from app.modules.storage.repository import StorageObjectRepository
from app.modules.storage.router import upload_file as storage_upload


def get_session_maker() -> Any:

    return AsyncSessionLocal


router = APIRouter()


@router.post(
    "/ingestion/upload",
    response_model=IngestionUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_and_ingest(
    background_tasks: BackgroundTasks,
    project_id: uuid.UUID = Query(...),
    version_id: Optional[uuid.UUID] = Query(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
    session_maker: Any = Depends(get_session_maker),
):

    # 1. Reuse Task #4 storage upload logic to securely store original
    storage_obj = await storage_upload(
        project_id=project_id, version_id=version_id, file=file, current_user=current_user, db=db
    )

    # 2. Initialize background job record
    job = await IngestionService.create_job(db, project_id, version_id, storage_obj.id)

    # 3. Add to background task worker
    background_tasks.add_task(IngestionService.run_ingestion_pipeline, session_maker, job.id)

    return IngestionUploadResponse(
        job_id=job.id, detail="Document successfully uploaded and queued for parsing"
    )


@router.post(
    "/ingestion/parse", response_model=IngestionUploadResponse, status_code=status.HTTP_202_ACCEPTED
)
async def trigger_parsing(
    background_tasks: BackgroundTasks,
    request_data: IngestionParseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
    session_maker: Any = Depends(get_session_maker),
):

    storage_repo = StorageObjectRepository(db)
    file_obj = await storage_repo.get_by_id(request_data.file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="Target storage object not found")

    if file_obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to parse this document")

    job = await IngestionService.create_job(
        db, request_data.project_id, request_data.version_id, request_data.file_id
    )

    background_tasks.add_task(IngestionService.run_ingestion_pipeline, session_maker, job.id)

    return IngestionUploadResponse(job_id=job.id, detail="Parsing job successfully triggered")


@router.get("/ingestion/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job = await IngestionService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found")

    # Access security validation
    storage_repo = StorageObjectRepository(db)
    file_obj = await storage_repo.get_by_id(job.file_id)
    if file_obj and file_obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied to job details")

    return job


@router.get("/ingestion/results/{job_id}")
async def get_job_results(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    job = await IngestionService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        return {
            "status": job.status,
            "progress": job.progress,
            "error_message": job.error_message,
            "detail": "Parsing has not completed yet.",
        }

    cdm_repo = CanonicalDocumentRepository(db)
    # Fetch result CDM representation
    cdm_doc = await cdm_repo.get_by_version(job.version_id or uuid.uuid4())
    if not cdm_doc:
        raise HTTPException(status_code=404, detail="Canonical document result not found")

    return {"status": "completed", "job_id": job_id, "cdm": cdm_doc}


@router.get("/ingestion/cdm/{version_id}", response_model=CanonicalDocument)
async def get_canonical_document_schema(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    cdm_repo = CanonicalDocumentRepository(db)
    cdm_doc = await cdm_repo.get_by_version(version_id)
    if not cdm_doc:
        raise HTTPException(status_code=404, detail="Canonical document not found for this version")

    return cdm_doc
