from __future__ import annotations

import pandas as pd
import streamlit as st

from src.application.services.tracker_service import TrackerService
from src.infrastructure.db.session import SessionLocal

st.set_page_config(page_title="Tracker", layout="wide")
st.title("Tracker")

status_filter = st.selectbox("Filter by ingestion status", ["all", "queued", "completed", "failed"], index=0)

db = SessionLocal()
try:
    jobs = TrackerService(db).list_jobs()
finally:
    db.close()

rows = [
    {
        "id": job.id,
        "company": job.company,
        "role": job.role,
        "source": job.source,
        "original_url": job.original_url,
        "ingestion_status": job.ingestion_status,
        "scrape_status": job.scrape_status,
        "analysis_status": job.analysis_status,
        "resume_status": job.resume_status,
        "created_at": job.created_at,
    }
    for job in jobs
]

if status_filter != "all":
    rows = [row for row in rows if row["ingestion_status"] == status_filter]

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
