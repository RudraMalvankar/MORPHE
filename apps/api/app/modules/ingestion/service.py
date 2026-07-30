import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.events import (
    DocumentParsedEvent,
    ParserFailedEvent,
    domain_event_bus,
)
from app.db.models import IngestionJobDb
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.ingestion.parsers import ParserFactory
from app.modules.storage.provider import LocalStorageProvider
from app.modules.storage.repository import StorageObjectRepository


class IngestionService:
    @staticmethod
    async def create_job(
        db: AsyncSession, project_id: uuid.UUID, version_id: Optional[uuid.UUID], file_id: uuid.UUID
    ) -> IngestionJobDb:

        job = IngestionJobDb(
            id=uuid.uuid4(),
            project_id=project_id,
            version_id=version_id,
            file_id=file_id,
            status="queued",
            progress=0,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job(db: AsyncSession, job_id: uuid.UUID) -> Optional[IngestionJobDb]:

        result = await db.execute(select(IngestionJobDb).where(IngestionJobDb.id == job_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def run_ingestion_pipeline(
        db_factory: Any,  # Async session maker
        job_id: uuid.UUID,
    ) -> None:

        # Run background parsing pipeline
        async with db_factory() as db:
            job = await IngestionService.get_job(db, job_id)
            if not job:
                return

            job.status = "running"
            job.progress = 10
            await db.commit()

            # 1. Fetch File Metadata
            storage_repo = StorageObjectRepository(db)
            file_obj = await storage_repo.get_by_id(job.file_id)
            if not file_obj:
                job.status = "failed"
                job.error_message = "Storage object not found"
                await db.commit()
                # Emit ParserFailedEvent
                event = ParserFailedEvent(
                    event_id=str(uuid.uuid4()), job_id=str(job_id), error="Storage object not found"
                )
                await domain_event_bus.publish(event)
                return

            job.progress = 30
            await db.commit()

            # 2. Read File Bytes
            provider = LocalStorageProvider(root_dir=settings.ORIGINAL_INPUTS_DIR)
            try:
                file_bytes = await provider.read_file(file_obj.storage_path)
            except Exception as e:
                job.status = "failed"
                job.error_message = f"Failed to read file from storage: {str(e)}"
                await db.commit()
                event = ParserFailedEvent(
                    event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e)
                )
                await domain_event_bus.publish(event)
                return

            job.progress = 50
            await db.commit()

            # 3. Determine and Execute Parser
            try:
                parser = ParserFactory.get_parser(file_obj.mime_type)
                cdm_doc = await parser.parse(
                    file_bytes,
                    project_id=str(job.project_id),
                    version_id=str(job.version_id or uuid.uuid4()),
                )
            except Exception as e:
                job.status = "failed"
                job.error_message = f"Parser failure: {str(e)}"
                await db.commit()
                event = ParserFailedEvent(
                    event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e)
                )
                await domain_event_bus.publish(event)
                return

            job.progress = 80
            await db.commit()

            # 4. Save CDM representation in DB (Task #2 repos)
            try:
                cdm_repo = CanonicalDocumentRepository(db)
                await cdm_repo.create_or_update(
                    version_id=job.version_id or uuid.uuid4(),
                    project_id=job.project_id,
                    doc=cdm_doc,
                )
            except Exception as e:
                job.status = "failed"
                job.error_message = f"CDM save failure: {str(e)}"
                await db.commit()
                event = ParserFailedEvent(
                    event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e)
                )
                await domain_event_bus.publish(event)
                return

            # Finalize completed job
            job.status = "completed"
            job.progress = 100
            await db.commit()

            # Publish Success Domain Events
            event_parsed = DocumentParsedEvent(
                event_id=str(uuid.uuid4()),
                project_id=str(job.project_id),
                version_id=str(job.version_id or ""),
            )
            await domain_event_bus.publish(event_parsed)
