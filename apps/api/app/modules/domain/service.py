import uuid
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    CitationStyleDetectedEvent,
    DomainAnalysisCompletedEvent,
    DomainAnalysisFailedEvent,
    DomainAnalysisStartedEvent,
    PrimaryDomainDetectedEvent,
    PublicationTypeDetectedEvent,
    ResearchTypeDetectedEvent,
    StructureAnalyzedEvent,
    SubdomainDetectedEvent,
    TerminologyExtractedEvent,
    domain_event_bus,
)
from app.db.models import (
    DomainDocDb,
    DomainJobDb,
    DomainStructureAnalysisDb,
    DomainTerminologyDb,
)
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.domain.pipeline import DomainPipelineRunner
from app.modules.domain.repository import DomainJobRepository
from app.modules.nlp.repository import (
    NlpDocumentRepository,
    NlpEntityRepository,
    NlpKeywordRepository,
)


class DomainService:
    @staticmethod
    async def create_job(
        db: AsyncSession, project_id: uuid.UUID, version_id: uuid.UUID
    ) -> DomainJobDb:
        job = DomainJobDb(
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
    async def run_domain_pipeline(db_factory: Any, job_id: uuid.UUID) -> None:
        async with db_factory() as db:
            job_repo = DomainJobRepository(db)
            job = await job_repo.get_by_id(job_id)
            if not job:
                return

            job.status = "running"
            job.progress = 10
            await db.commit()

            # Publish Started Event
            await domain_event_bus.publish(
                DomainAnalysisStartedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )

            # 1. Fetch CDM Document
            cdm_repo = CanonicalDocumentRepository(db)
            cdm_doc = await cdm_repo.get_by_version(job.version_id)
            if not cdm_doc:
                job.status = "failed"
                job.error_message = f"CDM not found for version {job.version_id}"
                await db.commit()
                await domain_event_bus.publish(
                    DomainAnalysisFailedEvent(
                        event_id=str(uuid.uuid4()), job_id=str(job_id), error=job.error_message
                    )
                )
                return

            # Combine CDM sections text
            text_parts = []
            for sec in cdm_doc.sections:
                text_parts.append(sec.title)
                text_parts.append(sec.content_markdown)
            raw_text = "\n\n".join(text_parts)

            job.progress = 30
            await db.commit()

            # 2. Fetch NLP Artifacts
            nlp_doc_repo = NlpDocumentRepository(db)
            nlp_doc = await nlp_doc_repo.get_by_version(job.version_id)

            nlp_dict: Dict[str, Any] = {"keywords": [], "entities": []}
            if nlp_doc:
                ent_repo = NlpEntityRepository(db)
                entities = await ent_repo.list_by_document(nlp_doc.id)
                nlp_dict["entities"] = [
                    {"entity_text": e.entity_text, "entity_type": e.entity_type} for e in entities
                ]

                kw_repo = NlpKeywordRepository(db)
                keywords = await kw_repo.list_by_document(nlp_doc.id)
                nlp_dict["keywords"] = [{"keyword": k.keyword, "score": k.score} for k in keywords]

            # 3. Run pipeline
            try:
                runner = DomainPipelineRunner()
                artifact = await runner.run(raw_text, cdm_doc.model_dump(), nlp_dict, {})
            except Exception as e:
                job.status = "failed"
                job.error_message = f"Domain pipeline execution failed: {str(e)}"
                await db.commit()
                await domain_event_bus.publish(
                    DomainAnalysisFailedEvent(
                        event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e)
                    )
                )
                return

            job.progress = 60
            await db.commit()

            # Dispatch intermediate events
            await domain_event_bus.publish(
                PrimaryDomainDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    primary_domain=artifact["primary_domain"],
                )
            )
            await domain_event_bus.publish(
                SubdomainDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    subdomain=artifact["subdomain"],
                )
            )

            # 4. Save to Database
            try:
                # Remove any existing domain documentation records for this version
                existing_recs = await db.execute(
                    select(DomainDocDb).where(DomainDocDb.version_id == job.version_id)
                )
                for row in existing_recs.scalars().all():
                    await db.delete(row)

                domain_doc = DomainDocDb(
                    id=uuid.uuid4(),
                    project_id=job.project_id,
                    version_id=job.version_id,
                    primary_domain=artifact["primary_domain"],
                    primary_domain_confidence=artifact["primary_domain_confidence"],
                    subdomain=artifact["subdomain"],
                    subdomain_confidence=artifact["subdomain_confidence"],
                    research_type=artifact["research_type"],
                    research_type_confidence=artifact["research_type_confidence"],
                    publication_type=artifact["publication_type"],
                    publication_type_confidence=artifact["publication_type_confidence"],
                    citation_style=artifact["citation_style"],
                    citation_style_confidence=artifact["citation_style_confidence"],
                )
                db.add(domain_doc)
                await db.flush()

                # Save Terminology Analysis
                for term in artifact.get("terminology", []):
                    term_db = DomainTerminologyDb(
                        id=uuid.uuid4(),
                        domain_doc_id=domain_doc.id,
                        term=term["term"],
                        frequency=term["frequency"],
                        term_type=term["term_type"],
                    )
                    db.add(term_db)

                # Save Structural Analysis
                s_analysis = artifact.get("structure_analysis", {})
                struct_db = DomainStructureAnalysisDb(
                    id=uuid.uuid4(),
                    domain_doc_id=domain_doc.id,
                    expected_sections=s_analysis.get("expected_sections", {}),
                    missing_sections=s_analysis.get("missing_sections", {}),
                    extra_sections=s_analysis.get("extra_sections", {}),
                    is_order_correct=s_analysis.get("is_order_correct", True),
                )
                db.add(struct_db)

                await db.commit()

            except Exception as e:
                job.status = "failed"
                job.error_message = f"Saving domain output records failed: {str(e)}"
                await db.commit()
                await domain_event_bus.publish(
                    DomainAnalysisFailedEvent(
                        event_id=str(uuid.uuid4()), job_id=str(job_id), error=str(e)
                    )
                )
                return

            job.status = "completed"
            job.progress = 100
            await db.commit()

            # Dispatch intermediate/end events
            await domain_event_bus.publish(
                ResearchTypeDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    research_type=artifact["research_type"],
                )
            )
            await domain_event_bus.publish(
                PublicationTypeDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    publication_type=artifact["publication_type"],
                )
            )
            await domain_event_bus.publish(
                CitationStyleDetectedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                    citation_style=artifact["citation_style"],
                )
            )
            await domain_event_bus.publish(
                TerminologyExtractedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                StructureAnalyzedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
            await domain_event_bus.publish(
                DomainAnalysisCompletedEvent(
                    event_id=str(uuid.uuid4()),
                    project_id=str(job.project_id),
                    version_id=str(job.version_id),
                )
            )
