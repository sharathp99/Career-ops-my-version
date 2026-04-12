from pathlib import Path

from src.infrastructure.exporters.pdf_exporter import export_pdf


def test_pdf_exporter_creates_file(monkeypatch, tmp_path) -> None:
    class FakeHTML:
        def __init__(self, string: str) -> None:
            self.string = string

        def write_pdf(self, path: str) -> None:
            Path(path).write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setitem(__import__("sys").modules, "weasyprint", type("M", (), {"HTML": FakeHTML}))
    output = tmp_path / "out.pdf"
    path = export_pdf("# Resume", "<html><body>{{ content|safe }}</body></html>", str(output))
    assert Path(path).exists()
