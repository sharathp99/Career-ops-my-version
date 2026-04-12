from __future__ import annotations

from bs4 import BeautifulSoup

from src.domain.schemas.jd_schemas import ScrapeResult
from src.infrastructure.scraping.base_scraper import BaseScraper


class LeverScraper(BaseScraper):
    source_platform = "lever"

    def can_handle(self, url: str) -> bool:
        return "jobs.lever.co" in url

    def scrape(self, url: str, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select_one(".posting-headline h2") or soup.select_one("h2")
        company = soup.select_one(".main-header-logo")
        location = soup.select_one(".posting-categories .location")
        description_node = soup.select_one(".posting-description") or soup
        return ScrapeResult(
            original_url=url,
            source_platform=self.source_platform,
            company=company.get_text(strip=True) if company else None,
            title=title.get_text(strip=True) if title else None,
            location=location.get_text(strip=True) if location else None,
            raw_description_text=description_node.get_text("\n", strip=True),
        )
