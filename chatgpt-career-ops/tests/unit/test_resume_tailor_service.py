from pathlib import Path

from src.application.services.resume_tailor_service import ResumeTailorService
from src.infrastructure.db.models import Job, JobAnalysis
from src.infrastructure.config.settings import get_settings


class FakeOpenAIClient:
    def generate_resume_markdown(self, prompt: str) -> str:
        assert "Master profile" in prompt
        return "# Alex Doe\n## Summary\nTailored resume from source evidence.\n"


def test_resume_tailor_creates_markdown(db_session, monkeypatch, tmp_path) -> None:
    job = Job(
        original_url="https://example.com/job/1",
        canonical_url="https://example.com/job/1",
        canonical_url_hash="x1",
        intake_method="manual",
        ingestion_status="queued",
        scrape_status="success",
        analysis_status="success",
        resume_status="pending",
    )
    db_session.add(job)
    db_session.flush()

    analysis = JobAnalysis(
        job_id=job.id,
        summary="Need python sql",
        responsibilities=["Build APIs"],
        required_qualifications=["Python", "SQL"],
        preferred_qualifications=[],
        technical_skills=["python", "sql"],
        keywords=["python", "sql"],
        domain_signals=["saas"],
        seniority_signals=["senior"],
    )
    db_session.add(analysis)
    db_session.commit()

    resume_path = tmp_path / "master.md"
    profile_path = tmp_path / "profile.json"
    resume_path.write_text("## Skills\nPython SQL", encoding="utf-8")
    profile_path.write_text('{"name":"Alex"}', encoding="utf-8")

    monkeypatch.setenv("MASTER_RESUME_PATH", str(resume_path))
    monkeypatch.setenv("MASTER_PROFILE_PATH", str(profile_path))

    get_settings.cache_clear()
    service = ResumeTailorService(db_session, openai_client=FakeOpenAIClient())
    response = service.generate_for_job(job.id)

    assert response.resume_status == "success"
    output = Path(response.output_folder)
    assert (output / "tailored_resume.md").exists()
    assert (output / "relevance_map.json").exists()


class HallucinatingClient:
    def generate_resume_markdown(self, prompt: str) -> str:
        return " ".join([f"inventedword{i}" for i in range(400)])


def test_no_hallucination_guard_marks_failed(db_session, monkeypatch, tmp_path) -> None:
    job = Job(
        original_url="https://example.com/job/2",
        canonical_url="https://example.com/job/2",
        canonical_url_hash="x2",
        intake_method="manual",
        ingestion_status="queued",
        scrape_status="success",
        analysis_status="success",
        resume_status="pending",
    )
    db_session.add(job)
    db_session.flush()
    db_session.add(
        JobAnalysis(
            job_id=job.id,
            summary="Need python",
            responsibilities=[],
            required_qualifications=["Python"],
            preferred_qualifications=[],
            technical_skills=["python"],
            keywords=["python"],
            domain_signals=[],
            seniority_signals=[],
        )
    )
    db_session.commit()

    resume_path = tmp_path / "master.md"
    profile_path = tmp_path / "profile.json"
    resume_path.write_text("## Skills\nPython", encoding="utf-8")
    profile_path.write_text('{"name":"Alex"}', encoding="utf-8")

    monkeypatch.setenv("MASTER_RESUME_PATH", str(resume_path))
    monkeypatch.setenv("MASTER_PROFILE_PATH", str(profile_path))

    get_settings.cache_clear()
    response = ResumeTailorService(db_session, openai_client=HallucinatingClient()).generate_for_job(job.id)
    assert response.resume_status == "failed"
    assert "No-hallucination guard failed" in response.message
