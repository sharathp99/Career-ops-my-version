from src.application.services.resume_match_service import ResumeMatchService
from src.domain.schemas.jd_schemas import JobAnalysisRead


def test_relevance_shortlisting() -> None:
    service = ResumeMatchService()
    resume = """## Summary\nPython API engineer\n## Experience\nWorked with SQL and AWS\n## Skills\nPython SQL Docker"""
    analysis = JobAnalysisRead(
        id=1,
        job_id=1,
        summary="Need Python SQL engineer",
        responsibilities=[],
        required_qualifications=["Python", "SQL"],
        preferred_qualifications=[],
        technical_skills=["python", "sql"],
        keywords=["python", "sql"],
        domain_signals=[],
        seniority_signals=[],
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )
    rel = service.build_relevance_map(job_id=1, jd_analysis=analysis, master_resume=resume)
    assert rel.shortlisted_sections
    assert rel.shortlisted_sections[0].score >= 1
