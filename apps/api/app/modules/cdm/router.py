import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_dependency
from app.db.models import User
from app.modules.auth.deps import get_current_user
from app.modules.cdm.schemas import CanonicalDocument
from app.modules.cdm.service import CDMService

router = APIRouter(prefix="/cdm", tags=["Canonical Document Model"])


class CDMUpdateRequest(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/{version_id}", response_model=CanonicalDocument)
async def get_cdm(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    service = CDMService(db)
    cdm = await service.get_cdm(version_id)
    if not cdm:
        raise HTTPException(status_code=404, detail="CDM not found for this version")
    return cdm


@router.patch("/{version_id}", response_model=CanonicalDocument)
async def update_cdm(
    version_id: uuid.UUID,
    data: CDMUpdateRequest,
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    service = CDMService(db)
    updates = data.model_dump(exclude_unset=True)
    cdm = await service.update_cdm(version_id, project_id, updates)
    if not cdm:
        raise HTTPException(status_code=404, detail="CDM not found for this version")
    return cdm


@router.get("/{version_id}/json")
async def get_cdm_json(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    service = CDMService(db)
    cdm_json = await service.get_cdm_json(version_id)
    if not cdm_json:
        raise HTTPException(status_code=404, detail="CDM not found for this version")
    return cdm_json


@router.get("/{version_id}/validate")
async def validate_cdm_structure(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    service = CDMService(db)
    result = await service.validate_structure(version_id)
    return result
