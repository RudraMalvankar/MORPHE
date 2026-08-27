from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class ACMPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "acm"

    @property
    def publisher_name(self) -> str:
        return "ACM"

    @property
    def latex_class(self) -> str:
        return "acmart"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="({authors}, {year})",
            reference_format='{authors}. {year}. {title}. {journal}, {volume}({issue}):{pages}.',
            order="alphabetical",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="letter",
            columns=2,
            column_gap="0.25in",
            margins={"top": "0.75in", "bottom": "1in", "left": "0.75in", "right": "0.75in"},
            font_family="Times New Roman",
            font_size="9pt",
            title_font_size="20pt",
            heading_font_size="10pt",
            line_spacing=1.0,
            abstract_font_size="9pt",
            references_font_size="8pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = " and ".join(citation.get("authors", [])[:3])
        return f'{authors}. {citation.get("year", "")}. {citation.get("title", "")}. {citation.get("journal", "")}, {citation.get("volume", "")}({citation.get("issue", "")}):{citation.get("pages", "")}.'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='column-count:2;font-size:9pt'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "us-letter", margin: (x: 0.75in, y: (top: 0.75in, bottom: 1in)))
#set text(font: "Times New Roman", size: 9pt)
#set par(leading: 0.65em, justify: true)

#align(center)[
  #text(size: 20pt, weight: "bold")[TITLE]
  #v(8pt)
  #text(size: 11pt)[Author Names]
]

#text(size: 9pt)[*Abstract*—Abstract text here.]

= Section Heading

Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"""
\documentclass[sigconf]{acmart}
\usepackage{graphicx}
\usepackage{booktabs}
"""

    def get_html_css(self) -> str:
        return """
body { font-family: 'Times New Roman', serif; font-size: 9pt; column-count: 2; max-width: 8.5in; margin: 0 auto; padding: 0.75in; }
h1 { font-size: 20pt; text-align: center; column-span: all; }
h2 { font-size: 10pt; }
"""
