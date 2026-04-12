from __future__ import annotations

from sqlalchemy.orm import Session

from src.infrastructure.repositories.job_repository import JobRepository


class TrackerService:
    def __init__(self, db: Session) -> None:
        self.repo = JobRepository(db)

    def list_jobs(self) -> list:
        return self.repo.list_jobs()

    def get_job(self, job_id: int):
        return self.repo.get(job_id)
