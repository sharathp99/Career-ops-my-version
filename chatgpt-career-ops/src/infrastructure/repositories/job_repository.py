from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import Job


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_hash(self, canonical_url_hash: str) -> Job | None:
        query = select(Job).where(Job.canonical_url_hash == canonical_url_hash)
        return self.db.execute(query).scalar_one_or_none()

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.flush()
        return job

    def list_jobs(self) -> list[Job]:
        query = select(Job).order_by(Job.created_at.desc())
        return list(self.db.execute(query).scalars().all())

    def list_pending_processing(self) -> list[Job]:
        query = select(Job).where(Job.scrape_status == "pending").order_by(Job.created_at.asc())
        return list(self.db.execute(query).scalars().all())

    def get(self, job_id: int) -> Job | None:
        return self.db.get(Job, job_id)

    def save(self, job: Job) -> Job:
        self.db.add(job)
        self.db.flush()
        return job
