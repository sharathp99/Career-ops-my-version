from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.application.services.batch_service import BatchService
from src.application.services.export_service import ExportService
from src.application.services.ingestion_service import IngestionService
from src.application.services.jd_analysis_service import JDAnalysisService
from src.application.services.resume_tailor_service import ResumeTailorService
from src.application.services.tracker_service import TrackerService
from src.infrastructure.db.base import Base
from src.infrastructure.db.session import SessionLocal, engine
from src.infrastructure.db import models  # noqa: F401
from src.infrastructure.repositories.job_repository import JobRepository


def cmd_health() -> None:
    print("ok")


def cmd_ingest(csv_path: str) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = IngestionService(db).ingest_csv_bytes(path.read_bytes())
        print(result.model_dump_json())
    finally:
        db.close()


def cmd_tracker() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        jobs = TrackerService(db).list_jobs()
        print(json.dumps([{"id": j.id, "url": j.original_url, "status": j.ingestion_status} for j in jobs], indent=2))
    finally:
        db.close()


def cmd_process(job_id: int) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        response = JDAnalysisService(db).process_job(job_id)
        print(response.model_dump_json())
    finally:
        db.close()


def cmd_process_batch() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = BatchService(db).process_pending_jobs()
        print(result.model_dump_json())
    finally:
        db.close()


def cmd_show_analysis(job_id: int) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        analysis = JDAnalysisService(db).get_analysis(job_id)
        if analysis is None:
            raise SystemExit("Analysis not found")
        print(analysis.model_dump_json())
    finally:
        db.close()


def cmd_generate_resume(job_id: int) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        response = ResumeTailorService(db).generate_for_job(job_id)
        print(response.model_dump_json())
    finally:
        db.close()


def cmd_generate_resumes_batch() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        jobs = JobRepository(db).list_jobs()
        service = ResumeTailorService(db)
        results = [service.generate_for_job(job.id).model_dump() for job in jobs if job.analysis_status == "success"]
        print(json.dumps(results, indent=2))
    finally:
        db.close()


def cmd_export(job_id: int) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        job = JobRepository(db).get(job_id)
        if not job or not job.output_folder:
            raise SystemExit("Output folder not found")
        path = ExportService().export_resume_pdf(job.output_folder)
        print(path)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="careerops")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--csv", required=True)
    sub.add_parser("tracker")

    process = sub.add_parser("process")
    process.add_argument("--job-id", required=True, type=int)

    sub.add_parser("process-batch")

    show_analysis = sub.add_parser("show-analysis")
    show_analysis.add_argument("--job-id", required=True, type=int)

    gen_resume = sub.add_parser("generate-resume")
    gen_resume.add_argument("--job-id", required=True, type=int)

    sub.add_parser("generate-resumes-batch")

    export_cmd = sub.add_parser("export")
    export_cmd.add_argument("--job-id", required=True, type=int)

    args = parser.parse_args()

    if args.command == "health":
        cmd_health()
    elif args.command == "ingest":
        cmd_ingest(args.csv)
    elif args.command == "tracker":
        cmd_tracker()
    elif args.command == "process":
        cmd_process(args.job_id)
    elif args.command == "process-batch":
        cmd_process_batch()
    elif args.command == "show-analysis":
        cmd_show_analysis(args.job_id)
    elif args.command == "generate-resume":
        cmd_generate_resume(args.job_id)
    elif args.command == "generate-resumes-batch":
        cmd_generate_resumes_batch()
    elif args.command == "export":
        cmd_export(args.job_id)


if __name__ == "__main__":
    main()
