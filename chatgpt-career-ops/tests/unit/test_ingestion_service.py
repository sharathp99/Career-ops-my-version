from src.application.services.ingestion_service import IngestionService


def test_duplicate_detection(db_session) -> None:
    service = IngestionService(db_session)
    urls = [
        "https://example.com/jobs/1?utm_source=abc",
        "https://example.com/jobs/1",
    ]
    result = service.ingest_raw_urls(urls)
    assert result.inserted == 1
    assert result.skipped == 1


def test_csv_ingestion(db_session) -> None:
    csv_bytes = b"job_url,company,role,source\nhttps://example.com/jobs/2,Acme,Engineer,linkedin\n"
    service = IngestionService(db_session)
    result = service.ingest_csv_bytes(csv_bytes)
    assert result.inserted == 1
    assert result.total_received == 1


def test_raw_url_ingestion_invalid_urls(db_session) -> None:
    service = IngestionService(db_session)
    result = service.ingest_raw_urls(["", "notaurl", "https://example.com/jobs/3"])
    assert result.inserted == 1
    assert result.invalid == 1
