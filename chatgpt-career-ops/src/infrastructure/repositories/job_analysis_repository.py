from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.schemas.jd_schemas import JDStructured
from src.infrastructure.db.models import JobAnalysis


class JobAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, job_id: int, structured: JDStructured) -> JobAnalysis:
        existing = self.get_by_job_id(job_id)
        payload = structured.model_dump()
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            self.db.flush()
            return existing

        analysis = JobAnalysis(job_id=job_id, **payload)
        self.db.add(analysis)
        self.db.flush()
        return analysis

    def get_by_job_id(self, job_id: int) -> JobAnalysis | None:
        query = select(JobAnalysis).where(JobAnalysis.job_id == job_id)
        return self.db.execute(query).scalar_one_or_none()
