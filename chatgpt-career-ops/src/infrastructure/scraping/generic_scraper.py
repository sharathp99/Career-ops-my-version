from __future__ import annotations

from bs4 import BeautifulSoup

from src.domain.schemas.jd_schemas import ScrapeResult
from src.infrastructure.scraping.base_scraper import BaseScraper
from src.utils.html_utils import html_to_text


class GenericScraper(BaseScraper):
    source_platform = "generic"

    def can_handle(self, url: str) -> bool:
        return True

    def scrape(self, url: str, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        return ScrapeResult(
            original_url=url,
            source_platform=self.source_platform,
            title=title,
            raw_description_text=html_to_text(html),
        )
