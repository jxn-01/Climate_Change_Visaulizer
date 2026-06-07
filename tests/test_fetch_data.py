import io
from pathlib import Path

import pytest
import scripts.fetch_data as fetch_data


class DummyResponse:
    def __init__(self, content: bytes):
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int = 8192):
        yield self._content


def test_download_file_saves_content(tmp_path, monkeypatch):
    target = tmp_path / "raw" / "test.csv"
    content = b"hello,world\n"

    def fake_get(url, stream=True, timeout=60):
        assert url == "https://example.com/test.csv"
        return DummyResponse(content)

    monkeypatch.setattr(fetch_data.requests, "get", fake_get)

    fetch_data.download_file("https://example.com/test.csv", target)

    assert target.exists()
    assert target.read_bytes() == content


def test_main_downloads_all_files(tmp_path, monkeypatch):
    saved = {}

    def fake_download_file(url, path):
        saved[path] = url
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")

    monkeypatch.setattr(fetch_data, "download_file", fake_download_file)
    monkeypatch.setattr(fetch_data, "RAW_DIR", tmp_path / "data" / "raw")

    fetch_data.main()

    assert len(saved) == len(fetch_data.DATA_FILES)
    for info in fetch_data.DATA_FILES.values():
        expected_path = tmp_path / "data" / "raw" / info["filename"]
        assert expected_path in saved
