from __future__ import annotations

from pydantic import BaseModel


class RelevanceItem(BaseModel):
    section_title: str
    score: float
    matched_keywords: list[str]
    content: str


class RelevanceMap(BaseModel):
    job_id: int
    shortlisted_sections: list[RelevanceItem]


class ResumeGenerationResponse(BaseModel):
    job_id: int
    resume_status: str
    output_folder: str | None = None
    message: str


class ResumeRead(BaseModel):
    job_id: int
    tailored_resume_markdown: str
    fit_summary_markdown: str
    output_folder: str
