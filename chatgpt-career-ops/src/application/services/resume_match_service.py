from __future__ import annotations

import json
import re
from pathlib import Path

from src.domain.schemas.jd_schemas import JobAnalysisRead
from src.domain.schemas.resume_schemas import RelevanceItem, RelevanceMap


class ResumeMatchService:
    def load_master_resume(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def load_master_profile(self, path: str) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _split_sections(self, resume_markdown: str) -> list[tuple[str, str]]:
        parts = re.split(r"(?m)^##\s+", resume_markdown)
        sections: list[tuple[str, str]] = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            lines = part.splitlines()
            title = lines[0].strip("# ")
            content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            sections.append((title, content))
        return sections

    def build_relevance_map(self, job_id: int, jd_analysis: JobAnalysisRead, master_resume: str) -> RelevanceMap:
        jd_text = " ".join(
            [
                jd_analysis.summary,
                " ".join(jd_analysis.keywords),
                " ".join(jd_analysis.technical_skills),
                " ".join(jd_analysis.required_qualifications),
            ]
        ).lower()
        jd_tokens = {token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", jd_text) if len(token) > 2}

        scored: list[RelevanceItem] = []
        for title, content in self._split_sections(master_resume):
            section_text = f"{title} {content}".lower()
            section_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", section_text))
            matched = sorted(token for token in jd_tokens.intersection(section_tokens))
            score = float(len(matched))
            if score > 0:
                scored.append(
                    RelevanceItem(
                        section_title=title,
                        score=score,
                        matched_keywords=matched[:20],
                        content=content,
                    )
                )

        shortlisted = sorted(scored, key=lambda x: x.score, reverse=True)[:6]
        return RelevanceMap(job_id=job_id, shortlisted_sections=shortlisted)
