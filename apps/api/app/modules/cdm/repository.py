import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import CDMUpdatedEvent, domain_event_bus
from app.db.models import CanonicalDocumentDb
from app.modules.cdm.schemas import CanonicalDocument


class CanonicalDocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_version(self, version_id: uuid.UUID) -> Optional[CanonicalDocument]:
        result = await self.db.execute(
            select(CanonicalDocumentDb).where(CanonicalDocumentDb.version_id == version_id)
        )
        db_doc = result.scalar_one_or_none()
        if db_doc:
            return CanonicalDocument.model_validate(db_doc.cdm_data)
        return None

    async def create_or_update(
        self, version_id: uuid.UUID, project_id: uuid.UUID, doc: CanonicalDocument
    ) -> CanonicalDocumentDb:
        result = await self.db.execute(
            select(CanonicalDocumentDb).where(CanonicalDocumentDb.version_id == version_id)
        )
        db_doc = result.scalar_one_or_none()

        cdm_json = doc.model_dump(mode="json")

        if db_doc:
            db_doc.cdm_data = cdm_json
        else:
            db_doc = CanonicalDocumentDb(id=uuid.uuid4(), version_id=version_id, cdm_data=cdm_json)
            self.db.add(db_doc)

        await self.db.commit()
        await self.db.refresh(db_doc)

        # Emit CDMUpdatedEvent
        event = CDMUpdatedEvent(
            event_id=str(uuid.uuid4()), project_id=str(project_id), version_id=str(version_id)
        )
        await domain_event_bus.publish(event)

        return db_doc
