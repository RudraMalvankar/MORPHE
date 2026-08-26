import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models import User
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository
from app.modules.projects.schemas import (
    PaperVersionResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.version_repo = PaperVersionRepository(db)

    async def create_project(
        self, user: User, data: ProjectCreate
    ) -> ProjectResponse:
        project = await self.project_repo.create(
            user_id=user.id,
            title=data.title,
            description=data.description,
            default_publisher_target=data.default_publisher_target,
        )
        logger.info(f"Project created: {project.id} by user {user.id}")
        return ProjectResponse.model_validate(project)

    async def list_user_projects(self, user: User) -> List[ProjectResponse]:
        projects = await self.project_repo.list_by_user(user.id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project(
        self, user: User, project_id: uuid.UUID
    ) -> Optional[ProjectDetailResponse]:
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.user_id != user.id:
            return None

        versions = await self.version_repo.list_by_project(project_id)
        version_responses = [
            PaperVersionResponse.model_validate(v) for v in versions
        ]

        return ProjectDetailResponse(
            id=str(project.id),
            title=project.title,
            description=project.description,
            default_publisher_target=project.default_publisher_target,
            created_at=project.created_at,
            updated_at=project.updated_at,
            versions=version_responses,
        )

    async def update_project(
        self, user: User, project_id: uuid.UUID, data: ProjectUpdate
    ) -> Optional[ProjectResponse]:
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.user_id != user.id:
            return None

        if data.title is not None:
            project.title = data.title
        if data.description is not None:
            project.description = data.description
        if data.default_publisher_target is not None:
            project.default_publisher_target = data.default_publisher_target

        await self.db.commit()
        await self.db.refresh(project)

        logger.info(f"Project updated: {project.id}")
        return ProjectResponse.model_validate(project)

    async def delete_project(
        self, user: User, project_id: uuid.UUID
    ) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.user_id != user.id:
            return False

        deleted = await self.project_repo.delete(project_id)
        if deleted:
            logger.info(f"Project deleted: {project_id}")
        return deleted

    async def get_project_versions(
        self, user: User, project_id: uuid.UUID
    ) -> Optional[List[PaperVersionResponse]]:
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.user_id != user.id:
            return None

        versions = await self.version_repo.list_by_project(project_id)
        return [PaperVersionResponse.model_validate(v) for v in versions]
