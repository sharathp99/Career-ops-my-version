from pathlib import Path


def test_process_job_endpoint(client, monkeypatch) -> None:
    client.post("/jobs/submit-urls", json={"urls": ["https://boards.greenhouse.io/acme/jobs/123"]})

    html = Path("tests/fixtures/sample_greenhouse.html").read_text(encoding="utf-8")

    def fake_fetch(self, _url: str) -> str:
        return html

    monkeypatch.setattr("src.application.services.jd_fetch_service.JDFetchService._fetch_html", fake_fetch)

    process_response = client.post("/jobs/process/1")
    assert process_response.status_code == 200
    body = process_response.json()
    assert body["scrape_status"] == "success"

    analysis_response = client.get("/jobs/1/analysis")
    assert analysis_response.status_code == 200
    assert analysis_response.json()["summary"]
