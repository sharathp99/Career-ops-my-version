def test_submit_urls_api(client) -> None:
    payload = {"urls": ["https://example.com/job/1", "https://example.com/job/1?utm_source=abc", "not-a-url"]}
    response = client.post("/jobs/submit-urls", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["inserted"] == 1
    assert body["skipped"] == 1
    assert body["invalid"] == 1


def test_upload_csv_api(client) -> None:
    content = "job_url,company,role,source\nhttps://example.com/job/2,Example,Engineer,linkedin\n"
    response = client.post(
        "/jobs/upload-csv",
        files={"file": ("jobs.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1
