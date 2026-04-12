from src.infrastructure.parsing.jd_cleaner import clean_jd_text


def test_jd_cleaner_removes_noise_and_whitespace() -> None:
    raw = "Responsibilities\n- Build\nPrivacy Policy\n\n\nTerms of Use"
    cleaned = clean_jd_text(raw)
    assert "Privacy" not in cleaned
    assert "Terms" not in cleaned
    assert "Responsibilities" in cleaned
