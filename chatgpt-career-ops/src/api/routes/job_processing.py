from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.application.services.batch_service import BatchService
from src.application.services.jd_analysis_service import JDAnalysisService
from src.domain.schemas.jd_schemas import BatchProcessResponse, JobAnalysisRead, ProcessResponse
from src.infrastructure.db.session import get_db

router = APIRouter(prefix="/jobs", tags=["job-processing"])


@router.post("/process/{job_id}", response_model=ProcessResponse)
def process_job(job_id: int, db: Session = Depends(get_db)) -> ProcessResponse:
    return JDAnalysisService(db).process_job(job_id)


@router.post("/process-batch", response_model=BatchProcessResponse)
def process_batch(db: Session = Depends(get_db)) -> BatchProcessResponse:
    return BatchService(db).process_pending_jobs()


@router.get("/{job_id}/analysis", response_model=JobAnalysisRead)
def get_job_analysis(job_id: int, db: Session = Depends(get_db)) -> JobAnalysisRead:
    analysis = JDAnalysisService(db).get_analysis(job_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
