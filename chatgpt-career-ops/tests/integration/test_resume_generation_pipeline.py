from pathlib import Path

from src.infrastructure.db.models import Job, JobAnalysis
from src.infrastructure.config.settings import get_settings


class FakeOpenAIClient:
    def generate_resume_markdown(self, prompt: str) -> str:
        return "# Alex Doe\n## Summary\nTailored markdown resume\n"


def test_resume_generation_pipeline(client, db_session, monkeypatch, tmp_path) -> None:
    job = Job(
        original_url="https://example.com/job/22",
        canonical_url="https://example.com/job/22",
        canonical_url_hash="h22",
        intake_method="manual",
        ingestion_status="queued",
        scrape_status="success",
        analysis_status="success",
        resume_status="pending",
        company="Acme",
        role="Backend Engineer",
    )
    db_session.add(job)
    db_session.flush()

    db_session.add(
        JobAnalysis(
            job_id=job.id,
            summary="Need Python SQL",
            responsibilities=["Build"],
            required_qualifications=["Python"],
            preferred_qualifications=[],
            technical_skills=["python", "sql"],
            keywords=["python", "sql"],
            domain_signals=["saas"],
            seniority_signals=["senior"],
        )
    )
    db_session.commit()

    resume_path = tmp_path / "master.md"
    profile_path = tmp_path / "profile.json"
    resume_path.write_text("## Skills\nPython SQL AWS", encoding="utf-8")
    profile_path.write_text('{"name":"Alex"}', encoding="utf-8")
    monkeypatch.setenv("MASTER_RESUME_PATH", str(resume_path))
    monkeypatch.setenv("MASTER_PROFILE_PATH", str(profile_path))

    get_settings.cache_clear()
    from src.api.routes import resumes as resumes_route

    monkeypatch.setattr(resumes_route, "ResumeTailorService", lambda db: __import__(
        "src.application.services.resume_tailor_service", fromlist=["ResumeTailorService"]
    ).ResumeTailorService(db, openai_client=FakeOpenAIClient()))

    response = client.post(f"/resumes/generate/{job.id}")
    assert response.status_code == 200
    assert response.json()["resume_status"] == "success"

    get_response = client.get(f"/resumes/{job.id}")
    assert get_response.status_code == 200
    assert "Tailored" in get_response.json()["tailored_resume_markdown"]
