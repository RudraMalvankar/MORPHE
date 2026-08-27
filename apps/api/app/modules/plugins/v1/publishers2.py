from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class OxfordPressPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "oxford"

    @property
    def publisher_name(self) -> str:
        return "Oxford University Press"

    @property
    def latex_class(self) -> str:
        return "ouparticle"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({authors}, {year})",
            reference_format='{authors}. {title}. {journal}. {year};{volume}({issue}):{pages}.',
            order="alphabetical",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'{authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{ouparticle}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class CambridgePressPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "cambridge"

    @property
    def publisher_name(self) -> str:
        return "Cambridge University Press"

    @property
    def latex_class(self) -> str:
        return "cambridge6"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({index})",
            reference_format='[{index}] {authors}. {title}. {journal}. {volume}({issue}):{pages}. {year}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}. {citation.get("year", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{cambridge6}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class FrontiersPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "frontiers"

    @property
    def publisher_name(self) -> str:
        return "Frontiers"

    @property
    def latex_class(self) -> str:
        return "frontiers"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {year};{volume}:{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=1, font_size="10pt", title_font_size="18pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}:{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 18pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{frontiers}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class CellPressPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "cell"

    @property
    def publisher_name(self) -> str:
        return "Cell Press"

    @property
    def latex_class(self) -> str:
        return "cell"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({index})",
            reference_format='[{index}] {authors}. {title}. {journal}. {volume}:{pages}. {year}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=2, font_size="9pt", title_font_size="18pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("volume", "")}:{citation.get("pages", "")}. {citation.get("year", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:9pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 9pt)\n#align(center)[#text(size: 18pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{cell}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:9pt;column-count:2;max-width:8.5in;margin:0 auto;padding:1in;}"


class BMJPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "bmj"

    @property
    def publisher_name(self) -> str:
        return "BMJ"

    @property
    def latex_class(self) -> str:
        return "bmj"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({index})",
            reference_format='[{index}] {authors}. {title}. {journal}. {year};{volume}:{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}:{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{bmj}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class JAMAPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "jama"

    @property
    def publisher_name(self) -> str:
        return "JAMA"

    @property
    def latex_class(self) -> str:
        return "jama"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({index})",
            reference_format='[{index}] {authors}. {title}. {journal}. {year};{volume}({issue}):{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=2, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{bmj}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;column-count:2;max-width:8.5in;margin:0 auto;padding:1in;}"
