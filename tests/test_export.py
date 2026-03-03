import csv
from pathlib import Path

from http_scrapper.export import save_to_csv_404, save_to_csv_http


class TestSaveToCsvHttp:
    def test_creates_csv_with_headers(self, tmp_path):
        filepath = tmp_path / "http.csv"
        save_to_csv_http(str(filepath), [])

        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            headers = next(reader)
        assert headers == ["Source page", "HTTP link found"]

    def test_writes_data_rows(self, tmp_path):
        filepath = tmp_path / "http.csv"
        data = [
            ("https://example.com", "http://example.com/page"),
            ("https://example.com/about", "http://cdn.example.com/img.jpg"),
        ]
        save_to_csv_http(str(filepath), data)

        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader)  # skip header
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["https://example.com", "http://example.com/page"]


class TestSaveToCsv404:
    def test_creates_csv_with_headers(self, tmp_path):
        filepath = tmp_path / "404.csv"
        save_to_csv_404(str(filepath), [])

        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            headers = next(reader)
        assert headers == ["Source page", "404 link"]

    def test_writes_data_rows(self, tmp_path):
        filepath = tmp_path / "404.csv"
        data = [("https://example.com", "https://example.com/broken")]
        save_to_csv_404(str(filepath), data)

        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader)  # skip header
            rows = list(reader)
        assert len(rows) == 1
        assert rows[0] == ["https://example.com", "https://example.com/broken"]

    def test_file_is_utf8_bom(self, tmp_path):
        filepath = tmp_path / "404.csv"
        save_to_csv_404(str(filepath), [])

        raw = Path(filepath).read_bytes()
        assert raw[:3] == b"\xef\xbb\xbf"
