from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from src.application.services.ingestion_service import IngestionService
from src.infrastructure.db.session import SessionLocal

st.set_page_config(page_title="Job Intake", layout="wide")
st.title("Job Intake")

uploaded = st.file_uploader("Upload CSV (job_url, company, role, source)", type=["csv"])
raw_urls = st.text_area("Paste job links (one per line)", height=180)

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.subheader("CSV Preview")
    st.dataframe(df, use_container_width=True)

if st.button("Ingest Jobs", type="primary"):
    db = SessionLocal()
    service = IngestionService(db)
    try:
        inserted = skipped = invalid = total = 0
        if uploaded is not None:
            uploaded.seek(0)
            result = service.ingest_csv_bytes(uploaded.read())
            inserted += result.inserted
            skipped += result.skipped
            invalid += result.invalid
            total += result.total_received
        if raw_urls.strip():
            url_lines = [line.strip() for line in io.StringIO(raw_urls).read().splitlines() if line.strip()]
            result = service.ingest_raw_urls(url_lines)
            inserted += result.inserted
            skipped += result.skipped
            invalid += result.invalid
            total += result.total_received
        st.success(f"Ingestion complete. Inserted={inserted}, Skipped={skipped}, Invalid={invalid}, Total={total}")
    finally:
        db.close()
