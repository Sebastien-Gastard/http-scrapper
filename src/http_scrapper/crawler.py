import sys
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.visited = set()
        self.http_links = []
        self.links_404 = []
        self.page_counter = 0

    def is_same_domain(self, base_url, target_url):
        return urlparse(base_url).netloc == urlparse(target_url).netloc

    def extract_links_and_resources(self, soup, current_url):
        tags_attrs = {
            "a": "href",
            "img": "src",
            "script": "src",
            "iframe": "src",
            "link": "href",
        }

        links = set()
        for tag, attr in tags_attrs.items():
            for element in soup.find_all(tag):
                link = element.get(attr)
                if link:
                    full_url = urljoin(current_url, link)
                    full_url, _ = urldefrag(full_url)
                    links.add(full_url)
        return links

    def crawl(self, url, base_url):
        url, _ = urldefrag(url)
        if url in self.visited:
            return
        self.visited.add(url)
        self.page_counter += 1
        print(f"[{self.page_counter}] Crawling: {url}")
        sys.stdout.flush()

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error on {url}: {e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        all_links = self.extract_links_and_resources(soup, url)

        for full_url in all_links:
            full_url, _ = urldefrag(full_url)
            parsed = urlparse(full_url)

            # Record HTTP links
            if parsed.scheme == "http":
                self.http_links.append((url, full_url))

            # Follow internal links (HTML only, skip JS)
            if parsed.scheme in ["http", "https"] and self.is_same_domain(
                base_url, full_url
            ):
                try:
                    response = requests.get(full_url, timeout=5)
                    response.raise_for_status()
                except requests.RequestException:
                    if (full_url, url) not in self.links_404:
                        self.links_404.append((url, full_url))
                    continue

                if not parsed.path.endswith(".js"):
                    self.crawl(full_url, base_url)
