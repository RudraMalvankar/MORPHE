from abc import ABC, abstractmethod
from typing import Any, Dict

from app.modules.export.schemas import CitationStyleConfig, LayoutRules


class BaseJournalPluginV1(ABC):
    @property
    @abstractmethod
    def api_version(self) -> str:
        return "v1"

    @property
    @abstractmethod
    def publisher_id(self) -> str:
        pass

    @property
    @abstractmethod
    def publisher_name(self) -> str:
        pass

    @property
    @abstractmethod
    def latex_class(self) -> str:
        pass

    @property
    @abstractmethod
    def citation_style(self) -> CitationStyleConfig:
        pass

    @abstractmethod
    def get_layout_rules(self) -> LayoutRules:
        pass

    @abstractmethod
    def format_citation(self, citation: Any, index: int) -> str:
        pass

    @abstractmethod
    def transform_sections(self, cdm: Any) -> Any:
        pass

    @abstractmethod
    def render_preview_html(self, cdm: Any) -> str:
        pass

    def get_typst_template(self) -> str:
        return ""

    def get_latex_preamble(self) -> str:
        return ""

    def get_docx_styles(self) -> Dict[str, Any]:
        return {}

    def get_html_css(self) -> str:
        return ""
