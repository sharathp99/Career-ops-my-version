from __future__ import annotations

from bs4 import BeautifulSoup

from src.domain.schemas.jd_schemas import ScrapeResult
from src.infrastructure.scraping.base_scraper import BaseScraper


class AshbyScraper(BaseScraper):
    source_platform = "ashby"

    def can_handle(self, url: str) -> bool:
        return "ashbyhq.com" in url

    def scrape(self, url: str, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select_one("h1")
        location = soup.find(string=lambda t: isinstance(t, str) and "location" in t.lower())
        body = soup.select_one("main") or soup
        return ScrapeResult(
            original_url=url,
            source_platform=self.source_platform,
            title=title.get_text(strip=True) if title else None,
            location=location.strip() if isinstance(location, str) else None,
            raw_description_text=body.get_text("\n", strip=True),
        )
