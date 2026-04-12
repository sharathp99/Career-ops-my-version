from src.application.services.jd_fetch_service import JDFetchService


def test_scraper_selection() -> None:
    service = JDFetchService()
    assert service.select_scraper("https://boards.greenhouse.io/x").source_platform == "greenhouse"
    assert service.select_scraper("https://jobs.lever.co/x").source_platform == "lever"
    assert service.select_scraper("https://jobs.ashbyhq.com/x").source_platform == "ashby"
    assert service.select_scraper("https://example.com/jobs/1").source_platform == "generic"
