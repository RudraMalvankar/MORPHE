from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseJournalPluginV1(ABC):
    @property
    @abstractmethod
    def api_version(self) -> str:
        return "v1"

    @property
    @abstractmethod
    def publisher_id(self) -> str:
        """Unique key e.g. 'ieee'"""
        pass

    @property
    @abstractmethod
    def publisher_name(self) -> str:
        """Display name e.g. 'IEEE Transactions'"""
        pass

    @abstractmethod
    def get_layout_rules(self) -> Dict[str, Any]:
        """Returns margins, column layouts, typography specs"""
        pass

    @abstractmethod
    def format_citation(self, citation: Any, index: int) -> str:
        """Formats citation item according to style rules"""
        pass

    @abstractmethod
    def transform_sections(self, cdm: Any) -> Any:
        """Applies publisher section ordering or title capitalization"""
        pass

    @abstractmethod
    def render_preview_html(self, cdm: Any) -> str:
        """Renders live HTML/CSS AST preview matching journal layout"""
        pass
