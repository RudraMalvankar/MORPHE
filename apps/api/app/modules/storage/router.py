import hashlib
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import db_dependency
from app.core.events import FileDownloadedEvent, domain_event_bus
from app.db.models import User
from app.modules.auth.deps import get_current_user
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository
from app.modules.storage.provider import LocalStorageProvider
from app.modules.storage.repository import StorageObjectRepository
from app.modules.storage.schemas import (
    StorageObjectResponse,
    StorageRestoreResponse,
    VersionFilesResponse,
)

router = APIRouter()

# Max upload size: 50MB (Part 10 Configuration)
MAX_UPLOAD_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".latex",
    ".tex",
    ".md",
    ".txt",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
}


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^\w\.\-]", "_", filename)
    return cleaned


def get_storage_provider() -> LocalStorageProvider:
    return LocalStorageProvider(root_dir=settings.ORIGINAL_INPUTS_DIR)


@router.post(
    "/storage/upload", response_model=StorageObjectResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    project_id: uuid.UUID = Query(...),
    version_id: Optional[uuid.UUID] = Query(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    # Extension verification (Part 3)
    import os

    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension {ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Size verification (Part 3)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum limit of 50MB",
        )

    # Ownership validation (Part 9 Security)
    proj_repo = ProjectRepository(db)
    project = await proj_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Generate SHA-256 Checksum (Part 4)
    checksum = hashlib.sha256(file_bytes).hexdigest()

    # Duplicate detection (Part 3)
    storage_repo = StorageObjectRepository(db)
    existing = await storage_repo.get_by_checksum(project_id, checksum)
    if existing:
        return existing

    # Save to storage provider (Part 2)
    provider = get_storage_provider()
    sanitized_name = sanitize_filename(file.filename or "uploaded_file")
    unique_storage_name = f"{uuid.uuid4()}{ext}"

    # Save file under project folders (Part 1 Layers)
    folder_path = f"project_{project_id}/version_{version_id or 'draft'}"
    storage_path = await provider.save_file(file_bytes, folder_path, unique_storage_name)

    # Log in database
    obj = await storage_repo.create_storage_object(
        project_id=project_id,
        version_id=version_id,
        owner_id=current_user.id,
        original_filename=sanitized_name,
        storage_filename=unique_storage_name,
        checksum=checksum,
        file_size=len(file_bytes),
        mime_type=file.content_type or "application/octet-stream",
        storage_provider="local",
        storage_path=storage_path,
    )
    return obj


@router.get("/storage/files", response_model=List[StorageObjectResponse])
async def list_files(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)
):
    storage_repo = StorageObjectRepository(db)
    all_files = await storage_repo.list_all()
    # Filter based on ownership or admin privilege (Part 9 Security)
    if current_user.role == "admin":
        return [f for f in all_files if not f.is_deleted]
    return [f for f in all_files if f.owner_id == current_user.id and not f.is_deleted]


@router.get("/storage/files/{file_id}", response_model=StorageObjectResponse)
async def get_file_metadata(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    storage_repo = StorageObjectRepository(db)
    obj = await storage_repo.get_by_id(file_id)
    if not obj or obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    if obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return obj


@router.get("/storage/files/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    storage_repo = StorageObjectRepository(db)
    obj = await storage_repo.get_by_id(file_id)
    if not obj or obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    if obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    provider = get_storage_provider()
    try:
        file_bytes = await provider.read_file(obj.storage_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File binary missing on storage provider")

    # Emit FileDownloadedEvent
    event = FileDownloadedEvent(
        event_id=str(uuid.uuid4()), file_id=str(file_id), user_id=str(current_user.id)
    )
    await domain_event_bus.publish(event)

    import io

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=obj.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{obj.original_filename}"'},
    )


@router.delete("/storage/files/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    storage_repo = StorageObjectRepository(db)
    obj = await storage_repo.get_by_id(file_id)
    if not obj or obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    if obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Soft delete (Part 5)
    await storage_repo.soft_delete(file_id)
    return {"detail": "File successfully deleted"}


@router.get("/storage/projects/{project_id}", response_model=List[StorageObjectResponse])
async def list_project_files(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    proj_repo = ProjectRepository(db)
    proj = await proj_repo.get_by_id(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if proj.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    storage_repo = StorageObjectRepository(db)
    files = await storage_repo.list_by_project(project_id)
    return files


@router.get("/storage/projects/{project_id}/versions", response_model=List[VersionFilesResponse])
async def list_project_versions(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    proj_repo = ProjectRepository(db)
    proj = await proj_repo.get_by_id(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if proj.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    ver_repo = PaperVersionRepository(db)
    versions = await ver_repo.list_by_project(project_id)

    storage_repo = StorageObjectRepository(db)
    response = []
    for v in versions:
        files = await storage_repo.list_by_version(v.id)
        files_schemas = [StorageObjectResponse.model_validate(f) for f in files]
        response.append(
            VersionFilesResponse(
                version_id=v.id,
                version_number=v.version_number,
                commit_message=v.commit_message,
                created_at=v.created_at,
                files=files_schemas,
            )
        )
    return response


@router.get("/storage/projects/{project_id}/history", response_model=List[StorageObjectResponse])
async def project_upload_history(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    # Audit history (Part 5)
    proj_repo = ProjectRepository(db)
    proj = await proj_repo.get_by_id(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if proj.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    storage_repo = StorageObjectRepository(db)
    # Include all objects (even deleted or archived) for audit trail
    all_objs = await storage_repo.list_all()
    project_history = [f for f in all_objs if f.project_id == project_id]
    return project_history


@router.patch("/storage/files/{file_id}/restore", response_model=StorageRestoreResponse)
async def restore_file_version(
    file_id: uuid.UUID,
    target_version_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    storage_repo = StorageObjectRepository(db)
    obj = await storage_repo.get_by_id(file_id)
    if not obj:
        raise HTTPException(status_code=404, detail="File not found")

    if obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    ver_repo = PaperVersionRepository(db)
    target_ver = await ver_repo.get_by_id(target_version_id)
    if not target_ver:
        raise HTTPException(status_code=404, detail="Target version not found")

    restored = await storage_repo.restore_version(file_id, target_version_id)
    if not restored:
        raise HTTPException(status_code=500, detail="Failed to restore file version")

    return StorageRestoreResponse(
        detail="File version successfully restored", file_id=file_id, version_id=target_version_id
    )
