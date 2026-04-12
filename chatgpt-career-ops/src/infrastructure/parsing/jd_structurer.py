from __future__ import annotations

from src.domain.schemas.jd_schemas import JDStructured
from src.infrastructure.parsing.keyword_extractor import extract_keywords


SECTION_HEADERS = {
    "responsibilities": ["responsibilities", "what you'll do", "what you will do"],
    "required_qualifications": ["requirements", "must have", "required qualifications"],
    "preferred_qualifications": ["preferred", "nice to have", "bonus"],
}


def _collect_bullets(lines: list[str], headers: list[str]) -> list[str]:
    items: list[str] = []
    collecting = False
    for line in lines:
        lower = line.lower().strip()
        if any(header in lower for header in headers):
            collecting = True
            continue
        if collecting and lower and not lower.startswith(("-", "•", "*")) and len(lower.split()) <= 3:
            collecting = False
        if collecting and lower.startswith(("-", "•", "*")):
            items.append(line.lstrip("-•* ").strip())
    return items


def structure_jd(clean_text: str) -> JDStructured:
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
    summary = " ".join(lines[:3])[:400] if lines else ""

    responsibilities = _collect_bullets(lines, SECTION_HEADERS["responsibilities"])
    required_qualifications = _collect_bullets(lines, SECTION_HEADERS["required_qualifications"])
    preferred_qualifications = _collect_bullets(lines, SECTION_HEADERS["preferred_qualifications"])
    technical_skills = extract_keywords(clean_text)

    lower_text = clean_text.lower()
    domain_signals = [word for word in ["fintech", "healthcare", "saas", "ecommerce", "ai"] if word in lower_text]
    seniority_signals = [
        word for word in ["senior", "staff", "lead", "principal", "manager", "entry-level"] if word in lower_text
    ]

    return JDStructured(
        summary=summary,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        preferred_qualifications=preferred_qualifications,
        technical_skills=technical_skills,
        keywords=technical_skills,
        domain_signals=domain_signals,
        seniority_signals=seniority_signals,
    )
