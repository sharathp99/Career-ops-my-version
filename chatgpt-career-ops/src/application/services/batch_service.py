from __future__ import annotations

from sqlalchemy.orm import Session

from src.application.services.jd_analysis_service import JDAnalysisService
from src.domain.schemas.jd_schemas import BatchProcessResponse
from src.infrastructure.repositories.job_repository import JobRepository


class BatchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.job_repo = JobRepository(db)
        self.analysis_service = JDAnalysisService(db)

    def process_pending_jobs(self) -> BatchProcessResponse:
        pending = self.job_repo.list_pending_processing()
        results = [self.analysis_service.process_job(job.id) for job in pending]
        failed = sum(1 for r in results if r.scrape_status == "failed")
        return BatchProcessResponse(total=len(pending), processed=len(results) - failed, failed=failed, results=results)
