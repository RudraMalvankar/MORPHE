import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.cdm.schemas import CanonicalDocument


class CDMService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cdm_repo = CanonicalDocumentRepository(db)

    async def get_cdm(self, version_id: uuid.UUID) -> Optional[CanonicalDocument]:
        return await self.cdm_repo.get_by_version(version_id)

    async def save_cdm(
        self,
        version_id: uuid.UUID,
        project_id: uuid.UUID,
        doc: CanonicalDocument,
    ) -> CanonicalDocument:
        await self.cdm_repo.create_or_update(version_id, project_id, doc)
        logger.info(f"CDM saved for version {version_id}")
        return doc

    async def update_cdm(
        self,
        version_id: uuid.UUID,
        project_id: uuid.UUID,
        updates: dict,
    ) -> Optional[CanonicalDocument]:
        existing = await self.cdm_repo.get_by_version(version_id)
        if not existing:
            return None

        update_data = updates
        updated_doc = existing.model_copy(update=update_data)
        await self.cdm_repo.create_or_update(version_id, project_id, updated_doc)
        logger.info(f"CDM updated for version {version_id}")
        return updated_doc

    async def get_cdm_json(self, version_id: uuid.UUID) -> Optional[dict]:
        cdm = await self.cdm_repo.get_by_version(version_id)
        if cdm:
            return cdm.model_dump(mode="json")
        return None

    async def validate_structure(self, version_id: uuid.UUID) -> dict:
        cdm = await self.cdm_repo.get_by_version(version_id)
        if not cdm:
            return {"valid": False, "errors": ["CDM not found for this version"]}

        errors = []
        warnings = []

        if not cdm.title or cdm.title == "Untitled":
            errors.append("Title is missing or generic")

        if not cdm.abstract or len(cdm.abstract) < 50:
            errors.append("Abstract is missing or too short (minimum 50 characters)")

        if not cdm.authors:
            warnings.append("No authors listed")

        if not cdm.sections:
            errors.append("Document has no sections")
        else:
            section_types = [s.section_type for s in cdm.sections]
            if "introduction" not in [s.value for s in section_types]:
                warnings.append("Missing Introduction section")
            if "conclusion" not in [s.value for s in section_types]:
                warnings.append("Missing Conclusion section")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "section_count": len(cdm.sections),
            "has_abstract": bool(cdm.abstract and len(cdm.abstract) > 50),
            "has_references": len(cdm.references) > 0,
            "author_count": len(cdm.authors),
        }
