# http-scrapper

A Python CLI tool that recursively crawls a website and:
- Detects all links using the insecure `http://` protocol
- Detects broken links (404 errors)

It scans multiple HTML elements: `<a>`, `<img>`, `<script>`, `<iframe>`, and `<link>`.

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-user>/http-scrapper.git
cd http-scrapper

# Create and activate a virtualenv
python -m venv env
source env/bin/activate

# Install the package
pip install -e .
```

## Usage

```bash
python -m http_scrapper https://www.example.com
```

Or via the installed console script:

```bash
http-scrapper https://www.example.com
```

## Output

Two timestamped CSV files are generated in the current directory:

- `http_links_{domain}_{timestamp}.csv` — all HTTP links found (source page + HTTP link)
- `404_links_{domain}_{timestamp}.csv` — all broken links found (source page + 404 link)

Example:
```
http_links_www_example_com_20250303-1430.csv
404_links_www_example_com_20250303-1430.csv
```

CSV files use semicolon delimiters and UTF-8 BOM encoding for Excel compatibility.

## Features

- Recursive crawling within the same domain
- Fragment URL deduplication
- 5-second timeout per request
- Real-time progress display with page counter

## Project Structure

```
src/http_scrapper/
├── __init__.py
├── __main__.py      # python -m entry point
├── cli.py           # Argparse CLI + orchestration
├── crawler.py       # Crawler class (crawl, link extraction, domain check)
└── export.py        # CSV export functions
tests/
├── test_crawler.py  # Unit tests for the crawler
└── test_export.py   # Unit tests for CSV export
```

## Development

```bash
# Install with dev dependencies (ruff, pytest, pytest-cov)
pip install -e ".[dev]"

# Lint & format
ruff check .
ruff format .

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## CI/CD

A GitHub Actions pipeline (`.github/workflows/ci.yml`) runs automatically on every push and pull request to `main`:

| Job    | Steps                                  |
|--------|----------------------------------------|
| **lint**  | `ruff check .` + `ruff format --check .` |
| **test**  | `pytest --cov` on Python 3.13          |
