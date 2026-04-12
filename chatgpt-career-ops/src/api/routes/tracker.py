from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.application.services.tracker_service import TrackerService
from src.domain.schemas.job_schemas import JobRead
from src.domain.schemas.tracker_schemas import TrackerResponse
from src.infrastructure.db.session import get_db

router = APIRouter(tags=["tracker"])


@router.get("/tracker", response_model=TrackerResponse)
def get_tracker(db: Session = Depends(get_db)) -> TrackerResponse:
    jobs = TrackerService(db).list_jobs()
    return TrackerResponse(total=len(jobs), jobs=[JobRead.model_validate(item) for item in jobs])
