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
