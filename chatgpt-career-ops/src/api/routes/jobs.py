from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.application.services.ingestion_service import IngestionService
from src.application.services.tracker_service import TrackerService
from src.domain.schemas.job_schemas import IngestionResponse, JobRead, URLSubmissionRequest
from src.infrastructure.db.session import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/upload-csv", response_model=IngestionResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> IngestionResponse:
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    content = await file.read()
    service = IngestionService(db)
    return service.ingest_csv_bytes(content)


@router.post("/submit-urls", response_model=IngestionResponse)
def submit_urls(payload: URLSubmissionRequest, db: Session = Depends(get_db)) -> IngestionResponse:
    service = IngestionService(db)
    return service.ingest_raw_urls(payload.urls)


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    service = TrackerService(db)
    return service.list_jobs()


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobRead:
    service = TrackerService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
