from __future__ import annotations

from pathlib import Path

import markdown2
from jinja2 import Template


def export_pdf(markdown_text: str, html_template: str, output_pdf_path: str) -> str:
    html_body = markdown2.markdown(markdown_text)
    html = Template(html_template).render(content=html_body)

    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError(f"PDF export dependency missing: {exc}") from exc

    output_path = Path(output_pdf_path)
    HTML(string=html).write_pdf(str(output_path))
    return str(output_path)
