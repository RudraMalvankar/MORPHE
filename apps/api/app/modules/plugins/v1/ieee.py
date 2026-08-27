from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class IEEEPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "ieee"

    @property
    def publisher_name(self) -> str:
        return "IEEE"

    @property
    def latex_class(self) -> str:
        return "IEEEtran"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}, "{title}," {journal}, vol. {volume}, no. {issue}, pp. {pages}, {year}.',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="letter",
            columns=2,
            column_gap="0.25in",
            margins={"top": "0.75in", "bottom": "1in", "left": "0.625in", "right": "0.625in"},
            font_family="Times New Roman",
            font_size="10pt",
            title_font_size="24pt",
            heading_font_size="10pt",
            line_spacing=1.0,
            abstract_font_size="9pt",
            references_font_size="8pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return (
            f'[{index}] {authors}, "{citation.get("title", "")}," '
            f'{citation.get("journal", "")}, vol. {citation.get("volume", "")}, '
            f'no. {citation.get("issue", "")}, pp. {citation.get("pages", "")}, '
            f'{citation.get("year", "")}.'
        )

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return self._render_two_column(cdm)

    def get_typst_template(self) -> str:
        return """
#set page(paper: "us-letter", margin: (x: 0.625in, y: (top: 0.75in, bottom: 1in)))
#set text(font: "Times New Roman", size: 10pt)
#set par(leading: 0.65em, justify: true)
#show heading: set text(size: 10pt, weight: "bold")
#show heading: set par(first-line-indent: 0pt)

#align(center)[
  #text(size: 24pt, weight: "bold")[TITLE]
  #v(6pt)
  #text(size: 11pt)[Author Names]
  #v(4pt)
  #text(size: 9pt)[*Abstract*—Abstract text here.]
  #v(4pt)
  #text(size: 8pt)[*Index Terms*—keyword1, keyword2]
]

#show heading.where(level: 1): it => [
  #v(8pt)
  #text(size: 10pt, weight: "bold")[#it.body]
  #v(4pt)
]

= Section Heading

Body text in two columns...
"""

    def get_latex_preamble(self) -> str:
        return r"""
\documentclass[journal]{IEEEtran}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{cite}
\usepackage{hyperref}
\usepackage{booktabs}
"""

    def get_html_css(self) -> str:
        return """
body { font-family: 'Times New Roman', serif; font-size: 10pt; max-width: 8.5in; margin: 0 auto; column-count: 2; column-gap: 0.25in; padding: 0.625in; }
h1 { font-size: 24pt; text-align: center; column-span: all; }
h2 { font-size: 10pt; font-weight: bold; }
.abstract { font-size: 9pt; text-align: justify; column-span: all; margin: 1em 2em; }
.references { font-size: 8pt; column-span: all; }
"""

    def _render_two_column(self, cdm: Any) -> str:
        return f"<div style='column-count:2'>{cdm}</div>"
