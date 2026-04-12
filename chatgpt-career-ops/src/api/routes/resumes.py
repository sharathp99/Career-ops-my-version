from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.application.services.export_service import ExportService
from src.application.services.resume_tailor_service import ResumeTailorService
from src.domain.schemas.resume_schemas import ResumeGenerationResponse, ResumeRead
from src.infrastructure.db.session import get_db
from src.infrastructure.repositories.job_repository import JobRepository

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/generate/{job_id}", response_model=ResumeGenerationResponse)
def generate_resume(job_id: int, db: Session = Depends(get_db)) -> ResumeGenerationResponse:
    return ResumeTailorService(db).generate_for_job(job_id)


@router.post("/generate-batch", response_model=list[ResumeGenerationResponse])
def generate_resumes_batch(db: Session = Depends(get_db)) -> list[ResumeGenerationResponse]:
    jobs = JobRepository(db).list_jobs()
    ready = [job for job in jobs if job.analysis_status == "success"]
    service = ResumeTailorService(db)
    return [service.generate_for_job(job.id) for job in ready]


@router.get("/{job_id}", response_model=ResumeRead)
def get_resume(job_id: int, db: Session = Depends(get_db)) -> ResumeRead:
    job = JobRepository(db).get(job_id)
    if not job or not job.output_folder:
        raise HTTPException(status_code=404, detail="Resume not found")

    folder = Path(job.output_folder)
    resume_path = folder / "tailored_resume.md"
    fit_path = folder / "fit_summary.md"
    if not resume_path.exists() or not fit_path.exists():
        raise HTTPException(status_code=404, detail="Resume artifacts missing")

    return ResumeRead(
        job_id=job.id,
        tailored_resume_markdown=resume_path.read_text(encoding="utf-8"),
        fit_summary_markdown=fit_path.read_text(encoding="utf-8"),
        output_folder=str(folder),
    )


@router.get("/{job_id}/download/pdf")
def download_resume_pdf(job_id: int, db: Session = Depends(get_db)) -> FileResponse:
    job = JobRepository(db).get(job_id)
    if not job or not job.output_folder:
        raise HTTPException(status_code=404, detail="Resume output not found")

    pdf_path = Path(job.output_folder) / "tailored_resume.pdf"
    if not pdf_path.exists():
        pdf_path_str = ExportService().export_resume_pdf(job.output_folder)
        pdf_path = Path(pdf_path_str)

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"tailored_resume_job_{job_id}.pdf")
