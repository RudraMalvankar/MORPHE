import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ExportArtifact


class ExportArtifactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, artifact_id: uuid.UUID) -> Optional[ExportArtifact]:
        result = await self.db.execute(
            select(ExportArtifact).where(ExportArtifact.id == artifact_id)
        )
        return result.scalar_one_or_none()

    async def list_by_version(self, version_id: uuid.UUID) -> List[ExportArtifact]:
        result = await self.db.execute(
            select(ExportArtifact).where(ExportArtifact.version_id == version_id)
        )
        return list(result.scalars().all())

    async def create(
        self, version_id: uuid.UUID, publisher_key: str, export_type: str, file_path: str
    ) -> ExportArtifact:
        artifact = ExportArtifact(
            id=uuid.uuid4(),
            version_id=version_id,
            publisher_key=publisher_key,
            export_type=export_type,
            file_path=file_path,
        )
        self.db.add(artifact)
        await self.db.commit()
        await self.db.refresh(artifact)
        return artifact
