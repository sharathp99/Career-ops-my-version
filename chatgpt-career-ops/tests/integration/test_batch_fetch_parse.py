from pathlib import Path


def test_batch_processing_and_artifacts(client, monkeypatch) -> None:
    client.post("/jobs/submit-urls", json={"urls": ["https://jobs.lever.co/acme/1", "https://example.com/jobs/2"]})

    html = Path("tests/fixtures/sample_lever.html").read_text(encoding="utf-8")

    def fake_fetch(self, _url: str) -> str:
        return html

    monkeypatch.setattr("src.application.services.jd_fetch_service.JDFetchService._fetch_html", fake_fetch)

    response = client.post("/jobs/process-batch")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["failed"] == 0
    assert list(Path("outputs").glob("*/*"))


def test_failed_scrape_updates_status(client, monkeypatch) -> None:
    client.post("/jobs/submit-urls", json={"urls": ["https://example.com/fail"]})

    def always_fail(self, _url: str) -> str:
        raise RuntimeError("network blocked")

    monkeypatch.setattr("src.application.services.jd_fetch_service.JDFetchService._fetch_html", always_fail)
    monkeypatch.setattr("src.infrastructure.scraping.playwright_fallback.fetch_with_playwright", lambda _url: None)

    response = client.post("/jobs/process/1")
    assert response.status_code == 200
    assert response.json()["scrape_status"] == "failed"

    tracker = client.get("/tracker").json()
    assert tracker["jobs"][0]["scrape_status"] == "failed"
