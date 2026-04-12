from __future__ import annotations

from pathlib import Path

from jinja2 import Template


def export_markdown(template_text: str, context: dict, output_path: str) -> str:
    rendered = Template(template_text).render(**context)
    Path(output_path).write_text(rendered, encoding="utf-8")
    return rendered
