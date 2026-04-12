from src.utils.url_utils import canonicalize_url, is_valid_url


def test_canonicalize_url_removes_tracking_params() -> None:
    url = "https://Example.com/jobs/123/?utm_source=x&b=2&a=1"
    assert canonicalize_url(url) == "https://example.com/jobs/123?a=1&b=2"


def test_is_valid_url() -> None:
    assert is_valid_url("https://example.com/job")
    assert not is_valid_url("example.com/job")
