from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.schemas.jd_schemas import ScrapeResult


class BaseScraper(ABC):
    source_platform: str = "generic"

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def scrape(self, url: str, html: str) -> ScrapeResult:
        raise NotImplementedError
