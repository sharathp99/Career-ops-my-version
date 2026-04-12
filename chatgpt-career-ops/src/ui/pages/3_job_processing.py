from __future__ import annotations

import streamlit as st

from src.application.services.batch_service import BatchService
from src.application.services.jd_analysis_service import JDAnalysisService
from src.application.services.tracker_service import TrackerService
from src.infrastructure.db.session import SessionLocal

st.set_page_config(page_title="Job Processing", layout="wide")
st.title("Job Processing")

db = SessionLocal()
try:
    tracker = TrackerService(db)
    jobs = tracker.list_jobs()
    queued_jobs = [job for job in jobs if job.scrape_status == "pending"]

    st.metric("Queued Jobs", len(queued_jobs))
    st.metric("Processed", len([job for job in jobs if job.scrape_status == "success"]))
    st.metric("Failed", len([job for job in jobs if job.scrape_status == "failed"]))

    if st.button("Process All Queued Jobs", type="primary"):
        result = BatchService(db).process_pending_jobs()
        st.success(f"Processed={result.processed}, Failed={result.failed}, Total={result.total}")

    job_options = {f"#{job.id} - {job.role or 'Unknown Role'}": job.id for job in queued_jobs}
    selected = st.selectbox("Process Single Job", options=list(job_options.keys()) if job_options else ["No queued jobs"])
    if job_options and st.button("Process Selected Job"):
        response = JDAnalysisService(db).process_job(job_options[selected])
        st.info(response.message)

    st.subheader("Structured Analysis Preview")
    chosen_id = st.number_input("Job ID", min_value=1, value=1, step=1)
    if st.button("Load Analysis"):
        analysis = JDAnalysisService(db).get_analysis(int(chosen_id))
        if analysis:
            st.json(analysis.model_dump())
        else:
            st.warning("Analysis not found for this job.")
finally:
    db.close()
