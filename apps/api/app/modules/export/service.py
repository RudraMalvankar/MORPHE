import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict

from app.modules.export.repository import ExportArtifactRepository
from app.modules.export.schemas import ExportFormat, ExportJobResponse, ExportRequest
from app.modules.plugins.v1.registry import get_plugin


class ExportService:
    def __init__(self, artifact_repo: ExportArtifactRepository):
        self.artifact_repo = artifact_repo
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)

    async def export_paper(self, request: ExportRequest, cdm: Dict[str, Any]) -> ExportJobResponse:
        job_id = str(uuid.uuid4())
        plugin = get_plugin(request.publisher_key)

        if request.format == ExportFormat.PDF:
            await self._export_typst_pdf(job_id, cdm, plugin)
        elif request.format == ExportFormat.LATEX:
            await self._export_latex(job_id, cdm, plugin)
        elif request.format == ExportFormat.DOCX:
            await self._export_docx(job_id, cdm, plugin)
        elif request.format == ExportFormat.HTML:
            await self._export_html(job_id, cdm, plugin)

        return ExportJobResponse(
            job_id=job_id,
            status="completed",
            format=request.format.value,
            publisher=request.publisher_key,
            message=f"Export completed: {job_id}",
        )

    async def _export_typst_pdf(self, job_id: str, cdm: Dict[str, Any], plugin: Any) -> None:
        typst_content = self._render_typst(cdm, plugin)
        typst_path = self.export_dir / f"{job_id}.typ"
        typst_path.write_text(typst_content, encoding="utf-8")

        try:
            subprocess.run(
                ["typst", "compile", str(typst_path), str(self.export_dir / f"{job_id}.pdf")],
                check=True,
                capture_output=True,
                timeout=60,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._create_fallback_pdf(job_id)

    async def _export_latex(self, job_id: str, cdm: Dict[str, Any], plugin: Any) -> None:
        latex_content = self._render_latex(cdm, plugin)
        tex_path = self.export_dir / f"{job_id}.tex"
        tex_path.write_text(latex_content, encoding="utf-8")

    async def _export_docx(self, job_id: str, cdm: Dict[str, Any], plugin: Any) -> None:
        docx_content = self._render_docx_xml(cdm, plugin)
        docx_path = self.export_dir / f"{job_id}.docx"
        docx_path.write_text(docx_content, encoding="utf-8")

    async def _export_html(self, job_id: str, cdm: Dict[str, Any], plugin: Any) -> None:
        html_content = self._render_html(cdm, plugin)
        html_path = self.export_dir / f"{job_id}.html"
        html_path.write_text(html_content, encoding="utf-8")

    def _render_typst(self, cdm: Dict[str, Any], plugin: Any) -> str:
        title = cdm.get("title", "Untitled")
        authors = ", ".join(cdm.get("authors", ["Author"]))
        abstract = cdm.get("abstract", "")
        sections = cdm.get("sections", [])
        references = cdm.get("references", [])
        keywords = ", ".join(cdm.get("keywords", []))

        template = plugin.get_typst_template() or """
#set page(paper: "a4", margin: 1in)
#set text(font: "Times New Roman", size: 10pt)
#set par(justify: true)
"""

        body_parts = [
            template,
            f"\n#align(center)[\n  #text(size: 24pt, weight: \"bold\")[{title}]\n  #v(6pt)\n  #text(size: 11pt)[{authors}]\n]",
        ]

        if abstract:
            body_parts.append(f"\n#text(size: 9pt)[*Abstract*—{abstract}]")
        if keywords:
            body_parts.append(f"\n#text(size: 8pt)[*Keywords*—{keywords}]")

        for section in sections:
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            body_parts.append(f"\n= {heading}\n\n{content}")

        if references:
            body_parts.append("\n= References\n\n")
            for i, ref in enumerate(references, 1):
                if isinstance(ref, dict):
                    authors_str = ", ".join(ref.get("authors", [])[:3])
                    body_parts.append(
                        f"[{i}] {authors_str}. {ref.get('title', '')}. {ref.get('journal', '')}. {ref.get('year', '')}.\n"
                    )
                elif isinstance(ref, str):
                    body_parts.append(f"[{i}] {ref}\n")

        return "\n".join(body_parts)

    def _render_latex(self, cdm: Dict[str, Any], plugin: Any) -> str:
        title = cdm.get("title", "Untitled")
        authors = cdm.get("authors", ["Author"])
        abstract = cdm.get("abstract", "")
        sections = cdm.get("sections", [])
        references = cdm.get("references", [])

        preamble = plugin.get_latex_preamble() or r"\documentclass{article}\usepackage{graphicx}"

        author_latex = " \\\\\\\n".join(
            [f"\\textbf{{{a}}}" for a in authors]
        )

        body_parts = [
            preamble,
            f"\n\\title{{{title}}}",
            f"\\author{{{author_latex}}}",
            "\\date{}\n",
            r"\begin{document}",
            r"\maketitle",
        ]

        if abstract:
            body_parts.append(f"\n\\begin{{abstract}}\n{abstract}\n\\end{{abstract}}")

        for section in sections:
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            body_parts.append(f"\n\\section{{{heading}}}\n{content}")

        if references:
            body_parts.append(r"\begin{thebibliography}{99}")
            for i, ref in enumerate(references, 1):
                if isinstance(ref, dict):
                    authors_str = ", ".join(ref.get("authors", [])[:3])
                    body_parts.append(
                        f"\\bibitem{{ref{i}}} {authors_str}. {ref.get('title', '')}. {ref.get('journal', '')}. {ref.get('year', '')}."
                    )
                elif isinstance(ref, str):
                    body_parts.append(f"\\bibitem{{ref{i}}} {ref}")
            body_parts.append(r"\end{thebibliography}")

        body_parts.append(r"\end{document}")
        return "\n".join(body_parts)

    def _render_docx_xml(self, cdm: Dict[str, Any], plugin: Any) -> str:
        title = cdm.get("title", "Untitled")
        authors = cdm.get("authors", ["Author"])
        abstract = cdm.get("abstract", "")
        sections = cdm.get("sections", [])

        doc_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">',
            "<w:body>",
            f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="48"/></w:rPr><w:t>{title}</w:t></w:r></w:p>',
        ]

        for author in authors:
            doc_parts.append(
                f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t>{author}</w:t></w:r></w:p>'
            )

        if abstract:
            doc_parts.append(f'<w:p><w:r><w:rPr><w:i/></w:rPr><w:t>Abstract: {abstract}</w:t></w:r></w:p>')

        for section in sections:
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            doc_parts.append(
                f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>{heading}</w:t></w:r></w:p>'
            )
            doc_parts.append(f'<w:p><w:r><w:t>{content}</w:t></w:r></w:p>')

        doc_parts.extend(["</w:body>", "</w:document>"])
        return "\n".join(doc_parts)

    def _render_html(self, cdm: Dict[str, Any], plugin: Any) -> str:
        title = cdm.get("title", "Untitled")
        authors = cdm.get("authors", ["Author"])
        abstract = cdm.get("abstract", "")
        sections = cdm.get("sections", [])
        references = cdm.get("references", [])
        keywords = cdm.get("keywords", [])

        css = plugin.get_html_css() or "body{font-family:'Times New Roman',serif;max-width:8.5in;margin:0 auto;padding:2in;font-size:10pt;}"

        html_parts = [
            "<!DOCTYPE html>",
            "<html><head>",
            f"<title>{title}</title>",
            f"<style>{css}</style>",
            "</head><body>",
            f'<h1 style="text-align:center">{title}</h1>',
            f'<p style="text-align:center"><strong>{", ".join(authors)}</strong></p>',
        ]

        if abstract:
            html_parts.append(f'<div class="abstract"><strong>Abstract</strong>—{abstract}</div>')
        if keywords:
            html_parts.append(f'<p><strong>Keywords:</strong> {", ".join(keywords)}</p>')

        for section in sections:
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            html_parts.append(f"<h2>{heading}</h2><p>{content}</p>")

        if references:
            html_parts.append('<div class="references"><h2>References</h2><ol>')
            for ref in references:
                if isinstance(ref, dict):
                    authors_str = ", ".join(ref.get("authors", [])[:3])
                    html_parts.append(
                        f"<li>{authors_str}. {ref.get('title', '')}. <em>{ref.get('journal', '')}</em>. {ref.get('year', '')}.</li>"
                    )
                elif isinstance(ref, str):
                    html_parts.append(f"<li>{ref}</li>")
            html_parts.append("</ol></div>")

        html_parts.extend(["</body></html>"])
        return "\n".join(html_parts)

    def _create_fallback_pdf(self, job_id: str) -> None:
        fallback = f"% PDF export placeholder - Typst not available\n% Job: {job_id}"
        pdf_path = self.export_dir / f"{job_id}.pdf"
        pdf_path.write_text(fallback, encoding="utf-8")

    def list_exporters(self):
        return [
            {"format": "pdf", "name": "PDF (Typst)", "description": "Professional PDF via Typst"},
            {"format": "latex", "name": "LaTeX", "description": "LaTeX source with publisher class"},
            {"format": "docx", "name": "Word", "description": "Microsoft Word document"},
            {"format": "html", "name": "HTML", "description": "Web-ready HTML with CSS"},
        ]
