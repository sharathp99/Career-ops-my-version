from fastapi import FastAPI

from src.api.routes.health import router as health_router
from src.api.routes.job_processing import router as job_processing_router
from src.api.routes.jobs import router as jobs_router
from src.api.routes.resumes import router as resumes_router
from src.api.routes.tracker import router as tracker_router


def create_app() -> FastAPI:
    app = FastAPI(title="chatgpt-career-ops", version="0.3.0")
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(tracker_router)
    app.include_router(job_processing_router)
    app.include_router(resumes_router)
    return app
