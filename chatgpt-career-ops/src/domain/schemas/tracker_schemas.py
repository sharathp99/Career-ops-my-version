from pydantic import BaseModel

from src.domain.schemas.job_schemas import JobRead


class TrackerResponse(BaseModel):
    total: int
    jobs: list[JobRead]
