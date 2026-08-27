from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class ACSPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "acs"

    @property
    def publisher_name(self) -> str:
        return "American Chemical Society"

    @property
    def latex_class(self) -> str:
        return "achemso"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="^{index}",
            reference_format='^{index}; {authors}. {title}. {journal}. {year}, {volume}, {pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = "; ".join(citation.get("authors", [])[:6])
        return f'^{{{index}}}; {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")}, {citation.get("volume", "")}, {citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{jacs}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class APSPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "aps"

    @property
    def publisher_name(self) -> str:
        return "American Physical Society"

    @property
    def latex_class(self) -> str:
        return "revtex4"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}, {title}. {journal} {volume}, {pages} ({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=2, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}, {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")}, {citation.get("pages", "")} ({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{revtex4}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;column-count:2;max-width:8.5in;margin:0 auto;padding:1in;}"


class SIAMPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "siam"

    @property
    def publisher_name(self) -> str:
        return "SIAM"

    @property
    def latex_class(self) -> str:
        return "siam"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}, {volume}:{pages}, {year}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="10pt", title_font_size="14pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}, {citation.get("volume", "")}:{citation.get("pages", "")}, {citation.get("year", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 14pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{siam}\usepackage{amsmath}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class IOPPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "iop"

    @property
    def publisher_name(self) -> str:
        return "IOP Publishing"

    @property
    def latex_class(self) -> str:
        return "iopart-num"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal} {volume} {pages} ({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=2, font_size="10pt", title_font_size="14pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")} {citation.get("pages", "")} ({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 14pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{iopart-num}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;column-count:2;max-width:8.5in;margin:0 auto;padding:1in;}"


class AMSPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "ams"

    @property
    def publisher_name(self) -> str:
        return "American Mathematical Society"

    @property
    def latex_class(self) -> str:
        return "amsart"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal} {volume}, {pages} ({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="10pt", title_font_size="14pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")}, {citation.get("pages", "")} ({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 14pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{amsart}\usepackage{amsmath}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class EmeraldPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "emerald"

    @property
    def publisher_name(self) -> str:
        return "Emerald"

    @property
    def latex_class(self) -> str:
        return "emerald"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {year}, {volume}({issue}), {pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")}, {citation.get("volume", "")}({citation.get("issue", "")}), {citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{emerald}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class SAGEPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "sage"

    @property
    def publisher_name(self) -> str:
        return "SAGE"

    @property
    def latex_class(self) -> str:
        return "sagej"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {year};{volume}({issue}):{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="10pt", title_font_size="14pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 14pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{sagej}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class AnnualReviewsPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "annual_reviews"

    @property
    def publisher_name(self) -> str:
        return "Annual Reviews"

    @property
    def latex_class(self) -> str:
        return "revtex4"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {volume}:{pages}({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="9pt", title_font_size="14pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("volume", "")}:{citation.get("pages", "")}({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:9pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 9pt)\n#align(center)[#text(size: 14pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{revtex4}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:9pt;max-width:8.5in;margin:0 auto;padding:1in;}"


class LancetPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "lancet"

    @property
    def publisher_name(self) -> str:
        return "The Lancet"

    @property
    def latex_class(self) -> str:
        return "lancet"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}. {title}. {journal}. {year};{volume}:{pages}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="a4", columns=2, font_size="9pt", title_font_size="18pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}. {citation.get("title", "")}. {citation.get("journal", "")}. {citation.get("year", "")};{citation.get("volume", "")}:{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:9pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"a4\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 9pt)\n#align(center)[#text(size: 18pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{lancet}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:9pt;column-count:2;max-width:8.5in;margin:0 auto;padding:1in;}"


class ScienceAAASPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "science"

    @property
    def publisher_name(self) -> str:
        return "Science (AAAS)"

    @property
    def latex_class(self) -> str:
        return "scicite"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({index})",
            reference_format='[{index}] {authors}, {title}. {journal} {volume}, {pages} ({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(page_size="letter", columns=1, font_size="10pt", title_font_size="16pt")

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}, {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")}, {citation.get("pages", "")} ({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return "#set page(paper: \"us-letter\", margin: 1in)\n#set text(font: \"Times New Roman\", size: 10pt)\n#align(center)[#text(size: 16pt, weight: \"bold\")[TITLE]]\n= Section\nBody..."

    def get_latex_preamble(self) -> str:
        return r"\documentclass{scicite}\usepackage{graphicx}"

    def get_html_css(self) -> str:
        return "body{font-family:'Times New Roman',serif;font-size:10pt;max-width:8.5in;margin:0 auto;padding:1in;}"
