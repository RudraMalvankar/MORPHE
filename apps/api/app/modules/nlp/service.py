import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    EntitiesExtractedEvent,
    KeywordsExtractedEvent,
    LanguageDetectedEvent,
    NLPCompletedEvent,
    NLPFailedEvent,
    NLPStartedEvent,
    StatisticsGeneratedEvent,
    TokenizationCompletedEvent,
    domain_event_bus,
)
from app.db.models import (
    NlpCitationMapDb,
    NlpDocumentDb,
    NlpEntityDb,
    NlpJobDb,
    NlpKeywordDb,
    NlpSectionClassificationDb,
    NlpStatisticsDb,
)
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.nlp.pipeline import NlpPipelineRunner
from app.modules.nlp.repository import NlpJobRepository


class NlpService:
    @staticmethod
    async def create_job(
        db: AsyncSession, project_id: uuid.UUID, version_id: uuid.UUID
    ) -> NlpJobDb:
        job = NlpJobDb(
            id=uuid.uuid4(),
            project_id=project_id,
            version_id=version_id,
            status="queued",
            progress=0,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def run_nlp_pipeline(db_factory: Any, job_id: uuid.UUID) -> None:
        async with db_factory() as db:
            job_repo = NlpJobRepository(db)
            job = await job_repo.get_by_id(job_id)
            if not job:
                return

            job.status = "running"
            job.progress = 10
            await db.commit()

            # Publish Started Event
            await domain_event_bus.publish(
                NLPStartedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )

            # 1. Retrieve Canonical Document Model (CDM)
            cdm_repo = CanonicalDocumentRepository(db)
            cdm_doc = await cdm_repo.get_by_version(job.version_id)
            if not cdm_doc:
                job.status = "failed"
                job.error_message = f"Canonical document not found for version {job.version_id}"
                await db.commit()
                await domain_event_bus.publish(
                    NLPFailedEvent(
                        event_id=str(uuid.uuid4()), job_id=str(job_id), error=job.error_message
                    )
                )
                return

            job.progress = 30
            await db.commit()

            # 2. Extract raw text from CDM sections to process linguistically
            text_parts = []
            for sec in cdm_doc.sections:
                text_parts.append(sec.title)
                text_parts.append(sec.content_markdown)
            raw_text = "\n\n".join(text_parts)

            # Convert CDM to dictionary format for pipeline compatibility
            cdm_dict = cdm_doc.model_dump()

            # 3. Run Pipeline Stages
            try:
                runner = NlpPipelineRunner()
                artifact = await runner.run(raw_text, cdm_dict)
            except Exception as e:
                job.status = "failed"
                job.error_message = f"Pipeline execution failed: {str(e)}"
                await db.commit()
                await domain_event_bus.publish(
                    NLPFailedEvent(event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e))
                )
                return

            job.progress = 60
            await db.commit()

            # Trigger intermediate phase completion events
            await domain_event_bus.publish(
                TokenizationCompletedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                LanguageDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    language=artifact.get("language", "en"),
                )
            )

            # 4. Save Extracted Artifacts to DB
            try:
                # Remove any existing NLP Documents for this version to avoid duplicates
                existing_doc = await db.execute(
                    select(NlpDocumentDb).where(NlpDocumentDb.version_id == job.version_id)
                )

                for row in existing_doc.scalars().all():
                    await db.delete(row)

                nlp_doc = NlpDocumentDb(
                    id=uuid.uuid4(),
                    project_id=job.project_id,
                    version_id=job.version_id,
                    language=artifact.get("language", "en"),
                    language_confidence=artifact.get("language_confidence", 1.0),
                )
                db.add(nlp_doc)
                await db.flush()  # Flush to populate ID

                # Save Entities
                for ent in artifact.get("entities", []):
                    entity_db = NlpEntityDb(
                        id=uuid.uuid4(),
                        document_id=nlp_doc.id,
                        entity_text=ent["text"],
                        entity_type=ent["type"],
                        confidence=ent["confidence"],
                    )
                    db.add(entity_db)

                # Save Keywords
                for kw in artifact.get("keywords", []):
                    keyword_db = NlpKeywordDb(
                        id=uuid.uuid4(),
                        document_id=nlp_doc.id,
                        keyword=kw["keyword"],
                        score=kw["score"],
                    )
                    db.add(keyword_db)

                # Save Statistics
                stats = artifact.get("statistics", {})
                stats_db = NlpStatisticsDb(
                    id=uuid.uuid4(),
                    document_id=nlp_doc.id,
                    word_count=stats.get("word_count", 0),
                    sentence_count=stats.get("sentence_count", 0),
                    paragraph_count=stats.get("paragraph_count", 0),
                    section_count=stats.get("section_count", 0),
                    avg_sentence_length=stats.get("avg_sentence_length", 0.0),
                    lexical_diversity=stats.get("lexical_diversity", 0.0),
                    vocabulary_size=stats.get("vocabulary_size", 0),
                    reading_time_mins=stats.get("reading_time_mins", 0.0),
                )
                db.add(stats_db)

                # Save Citation Maps
                for cmap in artifact.get("citation_mappings", []):
                    cmap_db = NlpCitationMapDb(
                        id=uuid.uuid4(),
                        document_id=nlp_doc.id,
                        citation_marker=cmap["marker"],
                        target_ref_id=cmap["target_ref_id"],
                    )
                    db.add(cmap_db)

                # Save Section Classifications
                for sclass in artifact.get("section_classifications", []):
                    sclass_db = NlpSectionClassificationDb(
                        id=uuid.uuid4(),
                        document_id=nlp_doc.id,
                        section_title=sclass["section_title"],
                        classified_type=sclass["classified_type"],
                        confidence=sclass["confidence"],
                    )
                    db.add(sclass_db)

                await db.commit()

            except Exception as e:
                job.status = "failed"
                job.error_message = f"Saving artifact models failed: {str(e)}"
                await db.commit()
                await domain_event_bus.publish(
                    NLPFailedEvent(event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e))
                )
                return

            # Finalize completion state
            job.status = "completed"
            job.progress = 100
            await db.commit()

            # Publish Intermediate & End events
            await domain_event_bus.publish(
                EntitiesExtractedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                KeywordsExtractedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                StatisticsGeneratedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                NLPCompletedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
