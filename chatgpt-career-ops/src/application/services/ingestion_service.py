from __future__ import annotations

import csv
import io

from sqlalchemy.orm import Session

from src.domain.schemas.job_schemas import IngestionResponse, JobCreate
from src.infrastructure.db.models import Job
from src.infrastructure.repositories.job_repository import JobRepository
from src.utils.hashing import sha256_hash
from src.utils.url_utils import canonicalize_url, is_valid_url


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.repo = JobRepository(db)
        self.db = db

    def ingest_url_rows(self, rows: list[JobCreate]) -> IngestionResponse:
        inserted = 0
        skipped = 0
        invalid = 0

        for row in rows:
            cleaned_url = row.original_url.strip()
            if not cleaned_url:
                skipped += 1
                continue
            if not is_valid_url(cleaned_url):
                invalid += 1
                continue

            canonical_url = canonicalize_url(cleaned_url)
            canonical_hash = sha256_hash(canonical_url)

            if self.repo.get_by_hash(canonical_hash):
                skipped += 1
                continue

            job = Job(
                original_url=cleaned_url,
                canonical_url=canonical_url,
                canonical_url_hash=canonical_hash,
                company=row.company,
                role=row.role,
                source=row.source,
                intake_method=row.intake_method,
                ingestion_status="queued",
                scrape_status="pending",
                analysis_status="pending",
                resume_status="pending",
            )
            self.repo.create(job)
            inserted += 1

        self.db.commit()
        return IngestionResponse(inserted=inserted, skipped=skipped, total_received=len(rows), invalid=invalid)

    def ingest_csv_bytes(self, content: bytes) -> IngestionResponse:
        text_stream = io.StringIO(content.decode("utf-8"))
        reader = csv.DictReader(text_stream)

        rows: list[JobCreate] = []
        for item in reader:
            rows.append(
                JobCreate(
                    original_url=(item.get("job_url") or "").strip(),
                    company=(item.get("company") or "").strip() or None,
                    role=(item.get("role") or "").strip() or None,
                    source=(item.get("source") or "").strip() or None,
                    intake_method="csv",
                )
            )
        return self.ingest_url_rows(rows)

    def ingest_raw_urls(self, urls: list[str]) -> IngestionResponse:
        rows = [JobCreate(original_url=url, intake_method="manual") for url in urls if url.strip()]
        return self.ingest_url_rows(rows)
