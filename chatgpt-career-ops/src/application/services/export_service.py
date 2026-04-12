from __future__ import annotations

from pathlib import Path

from src.infrastructure.exporters.pdf_exporter import export_pdf


class ExportService:
    def export_resume_pdf(self, output_folder: str) -> str:
        folder = Path(output_folder)
        resume_md_path = folder / "tailored_resume.md"
        if not resume_md_path.exists():
            raise RuntimeError("Tailored resume markdown not found")

        markdown_text = resume_md_path.read_text(encoding="utf-8")
        html_template = Path("src/infrastructure/templates/resume_template.html.j2").read_text(encoding="utf-8")
        pdf_path = folder / "tailored_resume.pdf"
        return export_pdf(markdown_text, html_template, str(pdf_path))
