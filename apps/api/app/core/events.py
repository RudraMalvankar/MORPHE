import datetime
from typing import Callable, Dict, List

from pydantic import BaseModel, Field

from app.core.logging import logger


class DomainEvent(BaseModel):
    event_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class DocumentIngestedEvent(DomainEvent):
    project_id: str
    version_id: str
    source_type: str


class CDMUpdatedEvent(DomainEvent):
    project_id: str
    version_id: str


class ValidationCompletedEvent(DomainEvent):
    project_id: str
    version_id: str
    compliance_score: int


class ExportRequestedEvent(DomainEvent):
    project_id: str
    version_id: str
    publisher_key: str
    format_type: str


# ==========================================
# PART 6 - KNOWLEDGE EVENTS
# ==========================================


class KnowledgeBaseEntryCreatedEvent(DomainEvent):
    category: str
    key: str


class KnowledgeBaseUpdatedEvent(DomainEvent):
    category: str
    key: str


class DomainProfileCreatedEvent(DomainEvent):
    key: str
    display_name: str


class DomainProfileUpdatedEvent(DomainEvent):
    key: str
    display_name: str


class PublisherAddedEvent(DomainEvent):
    key: str
    name: str


class JournalAddedEvent(DomainEvent):
    publisher_key: str
    key: str
    name: str


class CitationStyleAddedEvent(DomainEvent):
    key: str
    name: str


# ==========================================
# PART 7 - IAM EVENTS
# ==========================================


class UserRegisteredEvent(DomainEvent):
    user_id: str
    email: str


class UserLoggedInEvent(DomainEvent):
    user_id: str
    email: str


class UserLoggedOutEvent(DomainEvent):
    user_id: str


class PasswordChangedEvent(DomainEvent):
    user_id: str


class UserUpdatedEvent(DomainEvent):
    user_id: str


class UserDeletedEvent(DomainEvent):
    user_id: str


class RoleChangedEvent(DomainEvent):
    user_id: str
    new_role: str


class TokenRefreshedEvent(DomainEvent):
    user_id: str


# ==========================================
# PART 8 - STORAGE EVENTS
# ==========================================


class FileUploadedEvent(DomainEvent):
    file_id: str
    project_id: str
    filename: str


class FileDownloadedEvent(DomainEvent):
    file_id: str
    user_id: str


class FileDeletedEvent(DomainEvent):
    file_id: str
    project_id: str


class VersionCreatedEvent(DomainEvent):
    project_id: str
    version_id: str
    version_number: int


class VersionRestoredEvent(DomainEvent):
    project_id: str
    version_id: str
    restored_to_version_id: str


class ArtifactStoredEvent(DomainEvent):
    project_id: str
    version_id: str
    artifact_id: str
    publisher_key: str


class StorageProviderChangedEvent(DomainEvent):
    old_provider: str
    new_provider: str


# ==========================================
# PART 14 - INGESTION EVENTS
# ==========================================


class DocumentUploadedEvent(DomainEvent):
    project_id: str
    file_id: str


class DocumentDetectedEvent(DomainEvent):
    project_id: str
    file_id: str
    mime_type: str


class DocumentParsedEvent(DomainEvent):
    project_id: str
    version_id: str


class MetadataExtractedEvent(DomainEvent):
    project_id: str
    version_id: str


class CDMCreatedEvent(DomainEvent):
    project_id: str
    version_id: str


class ParserFailedEvent(DomainEvent):
    job_id: str
    error: str


# ==========================================
# PART 16 - NLP EVENTS
# ==========================================


class NLPStartedEvent(DomainEvent):
    project_id: str
    version_id: str


class SentenceExtractionCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class TokenizationCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class LanguageDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    language: str


class EntitiesExtractedEvent(DomainEvent):
    project_id: str
    version_id: str


class KeywordsExtractedEvent(DomainEvent):
    project_id: str
    version_id: str


class CitationAnalysisCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class SectionClassificationCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class StatisticsGeneratedEvent(DomainEvent):
    project_id: str
    version_id: str


class NLPCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class NLPFailedEvent(DomainEvent):
    job_id: str
    error: str


# ==========================================
# PART 17 - DOMAIN INTELLIGENCE EVENTS
# ==========================================


class DomainAnalysisStartedEvent(DomainEvent):
    project_id: str
    version_id: str


class PrimaryDomainDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    primary_domain: str


class SubdomainDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    subdomain: str


class ResearchTypeDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    research_type: str


class PublicationTypeDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    publication_type: str


class CitationStyleDetectedEvent(DomainEvent):
    project_id: str
    version_id: str
    citation_style: str


class TerminologyExtractedEvent(DomainEvent):
    project_id: str
    version_id: str


class StructureAnalyzedEvent(DomainEvent):
    project_id: str
    version_id: str


class DomainAnalysisCompletedEvent(DomainEvent):
    project_id: str
    version_id: str


class DomainAnalysisFailedEvent(DomainEvent):
    job_id: str
    error: str


EventHandler = Callable[[DomainEvent], None]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to event {event_type}")

    async def publish(self, event: DomainEvent):
        event_name = event.__class__.__name__
        logger.info(f"Publishing DomainEvent: {event_name} ({event.event_id})")
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error executing event handler {handler.__name__}: {e}")


domain_event_bus = EventBus()
