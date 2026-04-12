from __future__ import annotations

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from src.domain.schemas.jd_schemas import ScrapeResult
from src.infrastructure.scraping.ashby_scraper import AshbyScraper
from src.infrastructure.scraping.base_scraper import BaseScraper
from src.infrastructure.scraping.generic_scraper import GenericScraper
from src.infrastructure.scraping.greenhouse_scraper import GreenhouseScraper
from src.infrastructure.scraping.lever_scraper import LeverScraper
from src.infrastructure.scraping.playwright_fallback import fetch_with_playwright


class JDFetchService:
    def __init__(self) -> None:
        self.scrapers: list[BaseScraper] = [GreenhouseScraper(), LeverScraper(), AshbyScraper()]
        self.generic_scraper = GenericScraper()

    def select_scraper(self, url: str) -> BaseScraper:
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                return scraper
        return self.generic_scraper

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
    def _fetch_html(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def fetch_and_scrape(self, url: str) -> ScrapeResult:
        scraper = self.select_scraper(url)
        errors: list[str] = []

        try:
            html = self._fetch_html(url)
            result = scraper.scrape(url, html)
            if result.raw_description_text.strip():
                return result
            errors.append("primary scraper produced empty description")
        except Exception as exc:
            errors.append(f"primary scrape failed: {exc}")

        try:
            html = self._fetch_html(url)
            generic = self.generic_scraper.scrape(url, html)
            if generic.raw_description_text.strip():
                return generic
            errors.append("generic scraper produced empty description")
        except Exception as exc:
            errors.append(f"generic scrape failed: {exc}")

        playwright_html = fetch_with_playwright(url)
        if playwright_html:
            generic = self.generic_scraper.scrape(url, playwright_html)
            if generic.raw_description_text.strip():
                return generic

        raise RuntimeError(" ; ".join(errors) or "Unable to fetch job description")
