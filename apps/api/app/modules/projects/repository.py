import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import DocumentIngestedEvent, domain_event_bus
from app.db.models import OriginalInput, PaperVersion, Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id, Project.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(Project.user_id == user_id, Project.is_deleted.is_(False))
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        default_publisher_target: str = "ieee",
    ) -> Project:
        project = Project(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            default_publisher_target=default_publisher_target,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: uuid.UUID) -> bool:
        project = await self.get_by_id(project_id)
        if project:
            project.is_deleted = True
            await self.db.commit()
            return True
        return False


class PaperVersionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, version_id: uuid.UUID) -> Optional[PaperVersion]:
        result = await self.db.execute(select(PaperVersion).where(PaperVersion.id == version_id))
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> List[PaperVersion]:
        result = await self.db.execute(
            select(PaperVersion)
            .where(PaperVersion.project_id == project_id)
            .order_by(PaperVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        project_id: uuid.UUID,
        version_number: int,
        commit_message: str,
        input_type: str,
        file_path_or_text: str,
    ) -> PaperVersion:
        version = PaperVersion(
            id=uuid.uuid4(),
            project_id=project_id,
            version_number=version_number,
            commit_message=commit_message,
        )
        self.db.add(version)
        await self.db.flush()

        original_input = OriginalInput(
            id=uuid.uuid4(),
            version_id=version.id,
            input_type=input_type,
            file_path_or_text=file_path_or_text,
        )
        self.db.add(original_input)
        await self.db.commit()
        await self.db.refresh(version)

        # Emit DocumentIngestedEvent
        event = DocumentIngestedEvent(
            event_id=str(uuid.uuid4()),
            project_id=str(project_id),
            version_id=str(version.id),
            source_type=input_type,
        )
        await domain_event_bus.publish(event)

        return version
