from __future__ import annotations

from bs4 import BeautifulSoup

from src.domain.schemas.jd_schemas import ScrapeResult
from src.infrastructure.scraping.base_scraper import BaseScraper


class GreenhouseScraper(BaseScraper):
    source_platform = "greenhouse"

    def can_handle(self, url: str) -> bool:
        return "greenhouse.io" in url

    def scrape(self, url: str, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "html.parser")
        company = soup.select_one(".company-name")
        title = soup.select_one("h1.app-title") or soup.select_one("h1")
        location = soup.select_one(".location")
        description_node = soup.select_one("#content") or soup
        return ScrapeResult(
            original_url=url,
            source_platform=self.source_platform,
            company=company.get_text(strip=True) if company else None,
            title=title.get_text(strip=True) if title else None,
            location=location.get_text(strip=True) if location else None,
            raw_description_text=description_node.get_text("\n", strip=True),
        )
