from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class WileyPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "wiley"

    @property
    def publisher_name(self) -> str:
        return "Wiley"

    @property
    def latex_class(self) -> str:
        return "WileyNJD"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({authors}, {year})",
            reference_format='{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}.',
            order="alphabetical",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="a4", columns=1,
            margins={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            font_size="10pt", title_font_size="16pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'{authors} ({citation.get("year", "")}). {citation.get("title", "")}. {citation.get("journal", "")}, {citation.get("volume", "")}({citation.get("issue", "")}), {citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt;line-height:1.5'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "a4", margin: 1in)
#set text(font: "Times New Roman", size: 10pt)
#align(center)[#text(size: 16pt, weight: "bold")[TITLE]]
= Section Heading
Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"\documentclass{WileyNJD}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body { font-family: 'Times New Roman', serif; font-size: 10pt; max-width: 8.5in; margin: 0 auto; padding: 1in; }"


class TaylorFrancisPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "taylor_francis"

    @property
    def publisher_name(self) -> str:
        return "Taylor & Francis"

    @property
    def latex_class(self) -> str:
        return "tfcsv3"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {volume}({issue}):{pages}. {year}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="a4", columns=1,
            margins={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            font_size="10pt", title_font_size="16pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}. {citation.get("year", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt;line-height:1.5'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "a4", margin: 1in)
#set text(font: "Times New Roman", size: 10pt)
#align(center)[#text(size: 16pt, weight: "bold")[TITLE]]
= Section Heading
Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"\documentclass{tfcsv3}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body { font-family: 'Times New Roman', serif; font-size: 10pt; max-width: 8.5in; margin: 0 auto; padding: 1in; }"


class MDPIPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "mdpi"

    @property
    def publisher_name(self) -> str:
        return "MDPI"

    @property
    def latex_class(self) -> str:
        return "mdpi"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {year}; {volume}({issue}):{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="a4", columns=1,
            margins={"top": "0.75in", "bottom": "1in", "left": "0.75in", "right": "0.75in"},
            font_size="10pt", title_font_size="16pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")}; {citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt;line-height:1.5'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "a4", margin: (x: 0.75in, y: (top: 0.75in, bottom: 1in)))
#set text(font: "Times New Roman", size: 10pt)
#align(center)[#text(size: 16pt, weight: "bold")[TITLE]]
= Section Heading
Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"\documentclass{mdpi}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body { font-family: 'Times New Roman', serif; font-size: 10pt; max-width: 8.5in; margin: 0 auto; padding: 0.75in; }"


class PLOSPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "plos"

    @property
    def publisher_name(self) -> str:
        return "PLOS"

    @property
    def latex_class(self) -> str:
        return "plos"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors} ({year}) {title}. {journal} {volume}({issue}): {pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="a4", columns=1,
            margins={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            font_size="10pt", title_font_size="16pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors} ({citation.get("year", "")}) {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")}({citation.get("issue", "")}): {citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt;line-height:1.5'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "a4", margin: 1in)
#set text(font: "Times New Roman", size: 10pt)
#align(center)[#text(size: 16pt, weight: "bold")[TITLE]]
= Section Heading
Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"\documentclass{plos}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body { font-family: 'Times New Roman', serif; font-size: 10pt; max-width: 8.5in; margin: 0 auto; padding: 1in; }"
