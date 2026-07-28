import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    DomainEvent,
    DomainProfileCreatedEvent,
    DomainProfileUpdatedEvent,
    KnowledgeBaseEntryCreatedEvent,
    KnowledgeBaseUpdatedEvent,
    domain_event_bus,
)
from app.db.models import DomainProfileDb, KnowledgeBaseEntry
from app.db.repository import BaseRepository


class DomainProfileRepository(BaseRepository[DomainProfileDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(DomainProfileDb, db)

    async def get_by_key(self, key: str) -> Optional[DomainProfileDb]:
        result = await self.db.execute(select(DomainProfileDb).where(DomainProfileDb.key == key))
        return result.scalar_one_or_none()

    async def create_or_update(self, key: str, display_name: str, data: dict) -> DomainProfileDb:
        profile = await self.get_by_key(key)
        is_new = profile is None

        if profile:
            profile.display_name = display_name
            # For backward compatibility with TDD v1.0 mapping dictionary
            for dict_key, dict_val in data.items():
                if hasattr(profile, dict_key):
                    setattr(profile, dict_key, dict_val)
        else:
            profile = DomainProfileDb(id=uuid.uuid4(), key=key, display_name=display_name, **data)
            self.db.add(profile)

        await self.db.commit()
        await self.db.refresh(profile)

        # Emit events
        event: DomainEvent
        if is_new:
            event = DomainProfileCreatedEvent(
                event_id=str(uuid.uuid4()), key=key, display_name=display_name
            )
        else:
            event = DomainProfileUpdatedEvent(
                event_id=str(uuid.uuid4()), key=key, display_name=display_name
            )
        await domain_event_bus.publish(event)

        return profile


class KnowledgeBaseRepository(BaseRepository[KnowledgeBaseEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(KnowledgeBaseEntry, db)

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
        is_new = entry is None

        if entry:
            entry.value = value
        else:
            entry = KnowledgeBaseEntry(id=uuid.uuid4(), category=category, key=key, value=value)
            self.db.add(entry)

        await self.db.commit()
        await self.db.refresh(entry)

        # Emit events
        event: DomainEvent
        if is_new:
            event = KnowledgeBaseEntryCreatedEvent(
                event_id=str(uuid.uuid4()), category=category, key=key
            )
        else:
            event = KnowledgeBaseUpdatedEvent(
                event_id=str(uuid.uuid4()), category=category, key=key
            )
        await domain_event_bus.publish(event)

        return entry
