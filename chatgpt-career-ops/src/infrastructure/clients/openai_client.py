from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.infrastructure.config.settings import get_settings


class OpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key or None)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def generate_resume_markdown(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.2,
        )
        text = getattr(response, "output_text", "") or ""
        if not text.strip():
            raise RuntimeError("OpenAI returned empty response")
        return text.strip()


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def safe_log_metadata(prompt_name: str, model: str, response_text: str) -> str:
    metadata = {
        "prompt": prompt_name,
        "model": model,
        "response_chars": len(response_text),
    }
    return json.dumps(metadata)
