from src.infrastructure.parsing.keyword_extractor import extract_keywords


def test_keyword_extractor_returns_known_skills() -> None:
    text = "We use Python, SQL, Docker and Kubernetes with FastAPI"
    keywords = extract_keywords(text)
    assert "python" in keywords
    assert "sql" in keywords
    assert "docker" in keywords
