from __future__ import annotations

import re

COMMON_SKILLS = {
    "python", "sql", "aws", "docker", "kubernetes", "fastapi", "streamlit", "pandas", "spark", "airflow"
}


def extract_keywords(text: str, limit: int = 15) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}", text.lower())
    seen: list[str] = []
    for token in tokens:
        if token in COMMON_SKILLS and token not in seen:
            seen.append(token)
    return seen[:limit]
