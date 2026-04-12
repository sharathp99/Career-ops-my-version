from __future__ import annotations

import re

NOISE_PATTERNS = [
    r"privacy policy",
    r"terms of use",
    r"cookie",
    r"equal opportunity employer",
]


def clean_jd_text(text: str) -> str:
    cleaned = text
    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()
