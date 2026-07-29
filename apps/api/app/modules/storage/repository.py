import datetime
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    FileDeletedEvent,
    FileUploadedEvent,
    VersionRestoredEvent,
    domain_event_bus,
)
from app.db.models import StorageObject
from app.db.repository import BaseRepository


class StorageObjectRepository(BaseRepository[StorageObject]):
    def __init__(self, db: AsyncSession):
        super().__init__(StorageObject, db)

    async def get_by_checksum(
        self, project_id: uuid.UUID, checksum: str
    ) -> Optional[StorageObject]:
        # Duplicate detection (Part 3)
        result = await self.db.execute(
            select(StorageObject).where(
                StorageObject.project_id == project_id,
                StorageObject.checksum == checksum,
                StorageObject.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> List[StorageObject]:
        result = await self.db.execute(
            select(StorageObject).where(
                StorageObject.project_id == project_id, StorageObject.is_deleted.is_(False)
            )
        )
        return list(result.scalars().all())

    async def list_by_version(self, version_id: uuid.UUID) -> List[StorageObject]:
        result = await self.db.execute(
            select(StorageObject).where(
                StorageObject.version_id == version_id, StorageObject.is_deleted.is_(False)
            )
        )
        return list(result.scalars().all())

    async def create_storage_object(
        self,
        project_id: uuid.UUID,
        version_id: Optional[uuid.UUID],
        owner_id: uuid.UUID,
        original_filename: str,
        storage_filename: str,
        checksum: str,
        file_size: int,
        mime_type: str,
        storage_provider: str,
        storage_path: str,
    ) -> StorageObject:
        obj = StorageObject(
            id=uuid.uuid4(),
            project_id=project_id,
            version_id=version_id,
            owner_id=owner_id,
            original_filename=original_filename,
            storage_filename=storage_filename,
            checksum=checksum,
            file_size=file_size,
            mime_type=mime_type,
            storage_provider=storage_provider,
            storage_path=storage_path,
            status="active",
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

        # Emit FileUploadedEvent
        event = FileUploadedEvent(
            event_id=str(uuid.uuid4()),
            file_id=str(obj.id),
            project_id=str(project_id),
            filename=original_filename,
        )
        await domain_event_bus.publish(event)
        return obj

    async def soft_delete(self, file_id: uuid.UUID) -> bool:
        obj = await self.get_by_id(file_id)
        if not obj or obj.is_deleted:
            return False

        obj.is_deleted = True
        obj.deleted_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        obj.status = "deleted"
        await self.db.commit()

        # Emit FileDeletedEvent
        event = FileDeletedEvent(
            event_id=str(uuid.uuid4()), file_id=str(file_id), project_id=str(obj.project_id)
        )
        await domain_event_bus.publish(event)
        return True

    async def restore_version(
        self, file_id: uuid.UUID, target_version_id: uuid.UUID
    ) -> Optional[StorageObject]:
        obj = await self.get_by_id(file_id)
        if not obj:
            return None

        old_version_id = obj.version_id
        obj.version_id = target_version_id
        obj.is_deleted = False
        obj.deleted_at = None
        obj.status = "active"
        await self.db.commit()
        await self.db.refresh(obj)

        # Emit VersionRestoredEvent
        event = VersionRestoredEvent(
            event_id=str(uuid.uuid4()),
            project_id=str(obj.project_id),
            version_id=str(target_version_id),
            restored_to_version_id=str(old_version_id) if old_version_id else "",
        )
        await domain_event_bus.publish(event)
        return obj
