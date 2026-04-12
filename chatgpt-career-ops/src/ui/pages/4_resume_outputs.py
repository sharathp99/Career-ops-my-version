from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.services.export_service import ExportService
from src.application.services.resume_tailor_service import ResumeTailorService
from src.application.services.tracker_service import TrackerService
from src.infrastructure.db.session import SessionLocal

st.set_page_config(page_title="Resume Outputs", layout="wide")
st.title("Resume Outputs")

status_filter = st.selectbox("Filter resume status", ["all", "success", "failed", "pending"], index=0)

db = SessionLocal()
try:
    jobs = TrackerService(db).list_jobs()
    if status_filter != "all":
        jobs = [job for job in jobs if job.resume_status == status_filter]

    rows = [
        {
            "id": job.id,
            "company": job.company,
            "role": job.role,
            "resume_status": job.resume_status,
            "output_folder": job.output_folder,
        }
        for job in jobs
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    job_id = st.number_input("Job ID", min_value=1, value=1, step=1)

    if st.button("Generate Resume"):
        result = ResumeTailorService(db).generate_for_job(int(job_id))
        st.info(result.message)

    if st.button("Load Resume Preview"):
        selected = next((job for job in jobs if job.id == int(job_id)), None)
        if selected and selected.output_folder:
            folder = Path(selected.output_folder)
            resume_md = (folder / "tailored_resume.md")
            fit_md = (folder / "fit_summary.md")
            if resume_md.exists():
                st.subheader("Tailored Resume")
                st.markdown(resume_md.read_text(encoding="utf-8"))
            if fit_md.exists():
                st.subheader("Fit Summary")
                st.markdown(fit_md.read_text(encoding="utf-8"))

    if st.button("Export PDF"):
        selected = next((job for job in jobs if job.id == int(job_id)), None)
        if selected and selected.output_folder:
            pdf_path = ExportService().export_resume_pdf(selected.output_folder)
            st.success(f"PDF exported: {pdf_path}")
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", data=f.read(), file_name=f"tailored_resume_job_{job_id}.pdf")
finally:
    db.close()
