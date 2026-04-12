def test_tracker_retrieval(client) -> None:
    client.post("/jobs/submit-urls", json={"urls": ["https://example.com/job/4"]})
    response = client.get("/tracker")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["jobs"]) == 1
