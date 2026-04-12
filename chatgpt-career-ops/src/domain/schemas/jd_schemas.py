from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScrapeResult(BaseModel):
    original_url: str
    source_platform: str
    company: str | None = None
    title: str | None = None
    location: str | None = None
    employment_type: str | None = None
    raw_description_text: str


class JDStructured(BaseModel):
    summary: str
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    domain_signals: list[str] = Field(default_factory=list)
    seniority_signals: list[str] = Field(default_factory=list)


class JobAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    summary: str
    responsibilities: list[str]
    required_qualifications: list[str]
    preferred_qualifications: list[str]
    technical_skills: list[str]
    keywords: list[str]
    domain_signals: list[str]
    seniority_signals: list[str]
    created_at: datetime
    updated_at: datetime


class ProcessResponse(BaseModel):
    job_id: int
    scrape_status: str
    analysis_status: str
    message: str


class BatchProcessResponse(BaseModel):
    total: int
    processed: int
    failed: int
    results: list[ProcessResponse]
