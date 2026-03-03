import argparse
from datetime import datetime
from urllib.parse import urlparse

from http_scrapper.crawler import Crawler
from http_scrapper.export import save_to_csv_404, save_to_csv_http


def main():
    parser = argparse.ArgumentParser(
        description="Crawl a website and extract HTTP links."
    )
    parser.add_argument("start_url", help="Starting URL for the crawl")
    args = parser.parse_args()

    print("Starting crawl...\n")
    start_url = args.start_url

    crawler = Crawler()
    crawler.crawl(start_url, start_url)

    # Generate dynamic filenames
    domain = urlparse(start_url).netloc.replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename_http = f"http_links_{domain}_{timestamp}.csv"
    filename_404 = f"404_links_{domain}_{timestamp}.csv"

    print("\nCrawl complete.")
    save_to_csv_http(filename_http, crawler.http_links)
    print(
        f"\n{len(crawler.http_links)} HTTP links found. "
        f"Results saved to '{filename_http}'."
    )

    save_to_csv_404(filename_404, crawler.links_404)
    print(
        f"\n{len(crawler.links_404)} 404 links found. "
        f"Results saved to '{filename_404}'."
    )


if __name__ == "__main__":
    main()
