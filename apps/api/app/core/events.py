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
