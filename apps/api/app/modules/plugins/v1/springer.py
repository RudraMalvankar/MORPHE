from typing import Any

from app.modules.export.schemas import CitationStyleConfig, LayoutRules
from app.modules.plugins.v1.base import BaseJournalPluginV1


class SpringerPlugin(BaseJournalPluginV1):
    @property
    def api_version(self) -> str:
        return "v1"

    @property
    def publisher_id(self) -> str:
        return "springer"

    @property
    def publisher_name(self) -> str:
        return "Springer"

    @property
    def latex_class(self) -> str:
        return "svjour3"

    @property
    def citation_style(self) -> CitationStyleConfig:
        return CitationStyleConfig(
            in_text_format="[{index}]",
            reference_format='[{index}] {authors}, {title}. {journal} {volume}, {pages} ({year}).',
            order="numbered",
        )

    def get_layout_rules(self) -> LayoutRules:
        return LayoutRules(
            page_size="a4",
            columns=1,
            column_gap="0pt",
            margins={"top": "0.75in", "bottom": "1in", "left": "0.75in", "right": "0.75in"},
            font_family="Times New Roman",
            font_size="10pt",
            title_font_size="14pt",
            heading_font_size="11pt",
            line_spacing=1.2,
            abstract_font_size="9pt",
            references_font_size="8pt",
        )

    def format_citation(self, citation: Any, index: int) -> str:
        authors = ", ".join(citation.get("authors", [])[:6])
        return f'[{index}] {authors}, {citation.get("title", "")}. {citation.get("journal", "")} {citation.get("volume", "")}, {citation.get("pages", "")} ({citation.get("year", "")}).'

    def transform_sections(self, cdm: Any) -> Any:
        return cdm

    def render_preview_html(self, cdm: Any) -> str:
        return f"<div style='max-width:8.5in;margin:0 auto;font-size:10pt;line-height:1.2'>{cdm}</div>"

    def get_typst_template(self) -> str:
        return """
#set page(paper: "a4", margin: (x: 0.75in, y: (top: 0.75in, bottom: 1in)))
#set text(font: "Times New Roman", size: 10pt)
#set par(leading: 0.65em * 1.2, justify: true)

#align(center)[
  #text(size: 14pt, weight: "bold")[TITLE]
  #v(10pt)
]

= Section Heading

Body text...
"""

    def get_latex_preamble(self) -> str:
        return r"""
\documentclass{svjour3}
\usepackage{graphicx}
\usepackage{booktabs}
"""

    def get_html_css(self) -> str:
        return """
body { font-family: 'Times New Roman', serif; font-size: 10pt; line-height: 1.2; max-width: 8.5in; margin: 0 auto; padding: 0.75in; }
"""
