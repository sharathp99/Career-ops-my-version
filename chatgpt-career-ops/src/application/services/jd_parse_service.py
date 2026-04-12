from __future__ import annotations

from src.domain.schemas.jd_schemas import JDStructured
from src.infrastructure.parsing.jd_cleaner import clean_jd_text
from src.infrastructure.parsing.jd_structurer import structure_jd


class JDParseService:
    def clean(self, raw_text: str) -> str:
        return clean_jd_text(raw_text)

    def structure(self, clean_text: str) -> JDStructured:
        return structure_jd(clean_text)
