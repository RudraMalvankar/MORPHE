import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DomainDocDb, DomainJobDb, DomainStructureAnalysisDb, DomainTerminologyDb
from app.db.repository import BaseRepository


class DomainDocRepository(BaseRepository[DomainDocDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(DomainDocDb, db)

    async def get_by_version(self, version_id: uuid.UUID) -> Optional[DomainDocDb]:
        result = await self.db.execute(
            select(DomainDocDb).where(DomainDocDb.version_id == version_id)
        )
        return result.scalar_one_or_none()


class DomainTerminologyRepository(BaseRepository[DomainTerminologyDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(DomainTerminologyDb, db)

    async def list_by_document(self, domain_doc_id: uuid.UUID) -> List[DomainTerminologyDb]:
        result = await self.db.execute(
            select(DomainTerminologyDb).where(DomainTerminologyDb.domain_doc_id == domain_doc_id)
        )
        return list(result.scalars().all())


class DomainStructureAnalysisRepository(BaseRepository[DomainStructureAnalysisDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(DomainStructureAnalysisDb, db)

    async def get_by_document(
        self, domain_doc_id: uuid.UUID
    ) -> Optional[DomainStructureAnalysisDb]:
        result = await self.db.execute(
            select(DomainStructureAnalysisDb).where(
                DomainStructureAnalysisDb.domain_doc_id == domain_doc_id
            )
        )
        return result.scalar_one_or_none()


class DomainJobRepository(BaseRepository[DomainJobDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(DomainJobDb, db)

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[DomainJobDb]:
        result = await self.db.execute(select(DomainJobDb).where(DomainJobDb.id == job_id))
        return result.scalar_one_or_none()
