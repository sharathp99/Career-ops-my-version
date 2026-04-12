from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from src.application.services.resume_match_service import ResumeMatchService
from src.domain.schemas.resume_schemas import RelevanceMap, ResumeGenerationResponse
from src.infrastructure.clients.openai_client import OpenAIClient, load_prompt, safe_log_metadata
from src.infrastructure.config.settings import get_settings
from src.infrastructure.repositories.job_repository import JobRepository
from src.infrastructure.exporters.pdf_exporter import export_pdf


class ResumeTailorService:
    def __init__(self, db: Session, openai_client: OpenAIClient | None = None) -> None:
        self.db = db
        self.settings = get_settings()
        self.job_repo = JobRepository(db)
        self.match_service = ResumeMatchService()
        self.openai_client = openai_client or OpenAIClient()

    def _load_job_analysis_dict(self, job_id: int) -> dict:
        analysis_path = Path(f"outputs")
        for folder in analysis_path.glob("*"):
            file = folder / "jd_structured.json"
            if file.exists():
                data = json.loads(file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("job_id") == job_id:
                    return data
        raise RuntimeError("Structured analysis not found for job")

    def _build_prompt(self, template: str, job: object, relevance_map: RelevanceMap, master_profile: dict, jd_text: str) -> str:
        rel_json = json.dumps(relevance_map.model_dump(), indent=2)
        return (
            f"{template}\n\n"
            f"Target role/company:\n- role: {getattr(job, 'role', '')}\n- company: {getattr(job, 'company', '')}\n\n"
            f"Master profile:\n{json.dumps(master_profile, indent=2)}\n\n"
            f"Job description (cleaned):\n{jd_text}\n\n"
            f"Relevant source-of-truth resume sections:\n{rel_json}\n"
        )

    def generate_for_job(self, job_id: int) -> ResumeGenerationResponse:
        job = self.job_repo.get(job_id)
        if not job:
            return ResumeGenerationResponse(job_id=job_id, resume_status="failed", message="Job not found")
        if job.analysis_status != "success":
            return ResumeGenerationResponse(job_id=job_id, resume_status="failed", message="Job analysis not ready")

        try:
            from src.application.services.jd_analysis_service import JDAnalysisService

            analysis = JDAnalysisService(self.db).get_analysis(job_id)
            if analysis is None:
                raise RuntimeError("Analysis record not found")

            master_resume = self.match_service.load_master_resume(self.settings.master_resume_path)
            master_profile = self.match_service.load_master_profile(self.settings.master_profile_path)
            relevance = self.match_service.build_relevance_map(job_id=job_id, jd_analysis=analysis, master_resume=master_resume)

            out_dir = Path(self.settings.outputs_dir) / f"job-{job_id}"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "relevance_map.json").write_text(json.dumps(relevance.model_dump(), indent=2), encoding="utf-8")

            jd_cleaned_path = out_dir / "jd_cleaned.txt"
            jd_text = jd_cleaned_path.read_text(encoding="utf-8") if jd_cleaned_path.exists() else analysis.summary

            prompt_template = load_prompt("src/prompts/resume_tailor.txt")
            prompt = self._build_prompt(prompt_template, job, relevance, master_profile, jd_text)

            tailored_markdown = self.openai_client.generate_resume_markdown(prompt)
            metadata = safe_log_metadata("resume_tailor", self.settings.openai_model, tailored_markdown)

            master_resume_lines = set(master_resume.lower().split())
            generated_words = {w.lower() for w in tailored_markdown.split() if len(w) > 3}
            if len(generated_words.difference(master_resume_lines)) > 250:
                raise RuntimeError("No-hallucination guard failed: generated content diverges too much from source")

            fit_summary = (
                f"# Fit Summary\n\n"
                f"- Role: {job.role or 'Unknown'}\n"
                f"- Company: {job.company or 'Unknown'}\n"
                f"- Top strengths: {', '.join(analysis.technical_skills[:5])}\n"
                f"- Top gaps: {', '.join(analysis.required_qualifications[:3]) if analysis.required_qualifications else 'Not specified'}\n"
                f"- Recommendation: Proceed if strengths align with must-have requirements.\n"
            )

            (out_dir / "tailored_resume.md").write_text(tailored_markdown, encoding="utf-8")
            (out_dir / "fit_summary.md").write_text(fit_summary, encoding="utf-8")
            (out_dir / "analysis.json").write_text(json.dumps(analysis.model_dump(), indent=2), encoding="utf-8")
            (out_dir / "resume_generation_metadata.json").write_text(metadata, encoding="utf-8")

            html_template = Path("src/infrastructure/templates/resume_template.html.j2").read_text(encoding="utf-8")
            export_pdf(tailored_markdown, html_template, str(out_dir / "tailored_resume.pdf"))

            job.resume_status = "success"
            job.output_folder = str(out_dir)
            self.job_repo.save(job)
            self.db.commit()
            return ResumeGenerationResponse(
                job_id=job_id,
                resume_status=job.resume_status,
                output_folder=job.output_folder,
                message="Resume generated",
            )
        except Exception as exc:
            job.resume_status = "failed"
            job.notes = f"Resume generation failed: {exc}"
            self.job_repo.save(job)
            self.db.commit()
            return ResumeGenerationResponse(job_id=job_id, resume_status="failed", message=str(exc))
