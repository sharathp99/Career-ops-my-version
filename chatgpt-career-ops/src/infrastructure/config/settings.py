from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./career_ops.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    streamlit_server_port: int = 8501
    outputs_dir: str = "outputs"
    reports_dir: str = "reports"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4"
    master_resume_path: str = "data/sample_master_resume.md"
    master_profile_path: str = "data/sample_master_profile.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def ensure_directories(self) -> None:
        Path(self.outputs_dir).mkdir(parents=True, exist_ok=True)
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
