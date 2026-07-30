import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    NlpCitationMapDb,
    NlpDocumentDb,
    NlpEntityDb,
    NlpJobDb,
    NlpKeywordDb,
    NlpSectionClassificationDb,
    NlpStatisticsDb,
)
from app.db.repository import BaseRepository


class NlpDocumentRepository(BaseRepository[NlpDocumentDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpDocumentDb, db)

    async def get_by_version(self, version_id: uuid.UUID) -> Optional[NlpDocumentDb]:
        result = await self.db.execute(
            select(NlpDocumentDb).where(NlpDocumentDb.version_id == version_id)
        )
        return result.scalar_one_or_none()


class NlpEntityRepository(BaseRepository[NlpEntityDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpEntityDb, db)

    async def list_by_document(self, document_id: uuid.UUID) -> List[NlpEntityDb]:
        result = await self.db.execute(
            select(NlpEntityDb).where(NlpEntityDb.document_id == document_id)
        )
        return list(result.scalars().all())


class NlpKeywordRepository(BaseRepository[NlpKeywordDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpKeywordDb, db)

    async def list_by_document(self, document_id: uuid.UUID) -> List[NlpKeywordDb]:
        result = await self.db.execute(
            select(NlpKeywordDb).where(NlpKeywordDb.document_id == document_id)
        )
        return list(result.scalars().all())


class NlpStatisticsRepository(BaseRepository[NlpStatisticsDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpStatisticsDb, db)

    async def get_by_document(self, document_id: uuid.UUID) -> Optional[NlpStatisticsDb]:
        result = await self.db.execute(
            select(NlpStatisticsDb).where(NlpStatisticsDb.document_id == document_id)
        )
        return result.scalar_one_or_none()


class NlpCitationMapRepository(BaseRepository[NlpCitationMapDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpCitationMapDb, db)

    async def list_by_document(self, document_id: uuid.UUID) -> List[NlpCitationMapDb]:
        result = await self.db.execute(
            select(NlpCitationMapDb).where(NlpCitationMapDb.document_id == document_id)
        )
        return list(result.scalars().all())


class NlpSectionClassificationRepository(BaseRepository[NlpSectionClassificationDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpSectionClassificationDb, db)

    async def list_by_document(self, document_id: uuid.UUID) -> List[NlpSectionClassificationDb]:
        result = await self.db.execute(
            select(NlpSectionClassificationDb).where(
                NlpSectionClassificationDb.document_id == document_id
            )
        )
        return list(result.scalars().all())


class NlpJobRepository(BaseRepository[NlpJobDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(NlpJobDb, db)

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[NlpJobDb]:
        result = await self.db.execute(select(NlpJobDb).where(NlpJobDb.id == job_id))
        return result.scalar_one_or_none()
