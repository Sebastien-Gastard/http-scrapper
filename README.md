# http-scrapper

This Python script recursively crawls a website and:
- Extracts all links using the insecure `http://` protocol
- Detects broken links (404 errors)

It scans multiple HTML elements: `<a>`, `<img>`, `<script>`, `<iframe>`, and `<link>`.

## Prerequisites

Before running the script, make sure you have installed the required libraries:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with a target URL:

```bash
python http_crawler_404_check.py https://www.example.com
```

## Output

The script generates two CSV files with timestamped names:

- `liens_http_{domain}_{timestamp}.csv` - All HTTP links found (source page and HTTP link)
- `liens_404_{domain}_{timestamp}.csv` - All broken links found (source page and 404 link)

Example output files:
```
liens_http_www_example_com_20231215-1430.csv
liens_404_www_example_com_20231215-1430.csv
```

## Features

- Recursive crawling within the same domain
- Fragment URL deduplication
- 5-second timeout per request
- Real-time progress display with page counter
- CSV output with semicolon delimiter (Excel-compatible)
