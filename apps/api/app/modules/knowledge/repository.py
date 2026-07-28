import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DomainProfileDb, KnowledgeBaseEntry


class DomainProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_key(self, key: str) -> Optional[DomainProfileDb]:
        result = await self.db.execute(select(DomainProfileDb).where(DomainProfileDb.key == key))
        return result.scalar_one_or_none()

    async def list_all(self) -> List[DomainProfileDb]:
        result = await self.db.execute(select(DomainProfileDb))
        return list(result.scalars().all())

    async def create_or_update(self, key: str, display_name: str, data: dict) -> DomainProfileDb:
        profile = await self.get_by_key(key)
        if profile:
            profile.display_name = display_name
            profile.data = data
        else:
            profile = DomainProfileDb(
                id=uuid.uuid4(), key=key, display_name=display_name, data=data
            )
            self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile


class KnowledgeBaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entry(self, category: str, key: str) -> Optional[KnowledgeBaseEntry]:
        result = await self.db.execute(
            select(KnowledgeBaseEntry).where(
                KnowledgeBaseEntry.category == category, KnowledgeBaseEntry.key == key
            )
        )
        return result.scalar_one_or_none()

    async def list_by_category(self, category: str) -> List[KnowledgeBaseEntry]:
        result = await self.db.execute(
            select(KnowledgeBaseEntry).where(KnowledgeBaseEntry.category == category)
        )
        return list(result.scalars().all())

    async def create_or_update_entry(
        self, category: str, key: str, value: dict
    ) -> KnowledgeBaseEntry:
        entry = await self.get_entry(category, key)
        if entry:
            entry.value = value
        else:
            entry = KnowledgeBaseEntry(id=uuid.uuid4(), category=category, key=key, value=value)
            self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
