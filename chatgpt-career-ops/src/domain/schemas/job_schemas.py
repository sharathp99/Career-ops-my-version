from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    original_url: str
    company: str | None = None
    role: str | None = None
    source: str | None = None
    intake_method: str


class URLSubmissionRequest(BaseModel):
    urls: list[str] = Field(default_factory=list)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    canonical_url: str
    canonical_url_hash: str
    company: str | None
    role: str | None
    source: str | None
    intake_method: str
    ingestion_status: str
    scrape_status: str
    analysis_status: str
    resume_status: str
    notes: str | None
    output_folder: str | None
    created_at: datetime
    updated_at: datetime


class IngestionResponse(BaseModel):
    inserted: int
    skipped: int
    total_received: int
    invalid: int
