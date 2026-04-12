from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from src.application.services.jd_fetch_service import JDFetchService
from src.application.services.jd_parse_service import JDParseService
from src.domain.schemas.jd_schemas import JobAnalysisRead, ProcessResponse
from src.infrastructure.repositories.job_analysis_repository import JobAnalysisRepository
from src.infrastructure.repositories.job_repository import JobRepository
from src.utils.file_utils import ensure_dir
from src.utils.slugify import slugify


class JDAnalysisService:
    def __init__(self, db: Session, outputs_root: str = "outputs", reports_root: str = "reports") -> None:
        self.db = db
        self.fetch_service = JDFetchService()
        self.parse_service = JDParseService()
        self.job_repo = JobRepository(db)
        self.analysis_repo = JobAnalysisRepository(db)
        self.outputs_root = outputs_root
        self.reports_root = reports_root

    def _job_slug(self, job_id: int, company: str | None, role: str | None) -> str:
        name = "-".join([part for part in [company or "company", role or "role", str(job_id)] if part])
        return slugify(name)

    def _write_artifacts(self, slug: str, raw: str, clean: str, structured: dict) -> None:
        output_dir = Path(self.outputs_root) / slug
        report_dir = Path(self.reports_root) / slug
        ensure_dir(str(output_dir))
        ensure_dir(str(report_dir))

        (output_dir / "jd_raw.txt").write_text(raw, encoding="utf-8")
        (output_dir / "jd_cleaned.txt").write_text(clean, encoding="utf-8")
        (output_dir / "jd_structured.json").write_text(json.dumps(structured, indent=2), encoding="utf-8")

    def process_job(self, job_id: int) -> ProcessResponse:
        job = self.job_repo.get(job_id)
        if not job:
            return ProcessResponse(job_id=job_id, scrape_status="failed", analysis_status="failed", message="Job not found")

        try:
            scrape = self.fetch_service.fetch_and_scrape(job.original_url)
            raw_text = scrape.raw_description_text
            clean_text = self.parse_service.clean(raw_text)
            structured = self.parse_service.structure(clean_text)

            self.analysis_repo.upsert(job_id, structured)

            slug = self._job_slug(job.id, scrape.company or job.company, scrape.title or job.role)
            self._write_artifacts(slug, raw_text, clean_text, structured.model_dump())

            job.company = scrape.company or job.company
            job.role = scrape.title or job.role
            job.scrape_status = "success"
            job.analysis_status = "success"
            self.job_repo.save(job)
            self.db.commit()
            return ProcessResponse(
                job_id=job_id,
                scrape_status=job.scrape_status,
                analysis_status=job.analysis_status,
                message="Processed successfully",
            )
        except Exception as exc:
            job.scrape_status = "failed"
            job.analysis_status = "failed"
            job.notes = f"Processing failed: {exc}"
            self.job_repo.save(job)
            self.db.commit()
            return ProcessResponse(
                job_id=job_id,
                scrape_status=job.scrape_status,
                analysis_status=job.analysis_status,
                message=str(exc),
            )

    def get_analysis(self, job_id: int) -> JobAnalysisRead | None:
        analysis = self.analysis_repo.get_by_job_id(job_id)
        if not analysis:
            return None
        return JobAnalysisRead.model_validate(analysis)
