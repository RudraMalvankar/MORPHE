import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import ValidationCompletedEvent, domain_event_bus
from app.db.models import ValidationReport
from app.db.repository import BaseRepository


class ValidationReportRepository(BaseRepository[ValidationReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(ValidationReport, db)

    async def get_by_version(self, version_id: uuid.UUID) -> Optional[ValidationReport]:
        result = await self.db.execute(
            select(ValidationReport).where(ValidationReport.version_id == version_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, version_id: uuid.UUID, project_id: uuid.UUID, compliance_score: int, issues: dict
    ) -> ValidationReport:
        report = ValidationReport(
            id=uuid.uuid4(),
            version_id=version_id,
            compliance_score=compliance_score,
            issues_json=issues,
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        # Emit ValidationCompletedEvent
        event = ValidationCompletedEvent(
            event_id=str(uuid.uuid4()),
            project_id=str(project_id),
            version_id=str(version_id),
            compliance_score=compliance_score,
        )
        await domain_event_bus.publish(event)

        return report
