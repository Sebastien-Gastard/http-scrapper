import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class Crawler:
    def __init__(self, max_workers=10, timeout=30):
        self.visited = set()
        self.checked_external = set()
        self.http_links = []
        self.links_404 = []
        self.page_counter = 0
        self.max_workers = max_workers
        self.timeout = timeout
        self.lock = threading.Lock()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

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

    def _check_external(self, source_url, target_url):
        try:
            response = self.session.head(target_url, timeout=self.timeout)
            if response.status_code == 404:
                with self.lock:
                    self.links_404.append((source_url, target_url))
        except requests.RequestException:
            pass

    def _process_page(self, url, base_url, source_url=None):
        with self.lock:
            self.page_counter += 1
            counter = self.page_counter
        print(f"[{counter}] Crawling: {url}")
        sys.stdout.flush()

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error on {url}: {e}")
            if source_url:
                with self.lock:
                    self.links_404.append((source_url, url))
            return [], []

        soup = BeautifulSoup(response.text, "html.parser")
        all_links = self.extract_links_and_resources(soup, url)

        internal_urls = []  # (source_url, target_url)
        external_checks = []  # (source_url, target_url)
        for full_url in all_links:
            full_url, _ = urldefrag(full_url)
            parsed = urlparse(full_url)

            if parsed.scheme == "http":
                with self.lock:
                    self.http_links.append((url, full_url))

            if parsed.scheme not in ("http", "https"):
                continue

            if self.is_same_domain(base_url, full_url):
                if not parsed.path.endswith((".js", ".svg")):
                    internal_urls.append((url, full_url))
            else:
                with self.lock:
                    if full_url not in self.checked_external:
                        self.checked_external.add(full_url)
                        external_checks.append((url, full_url))

        return internal_urls, external_checks

    def crawl(self, url, base_url):
        url, _ = urldefrag(url)
        if url in self.visited:
            return
        self.visited.add(url)

        pending = set()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit first page
            future = executor.submit(self._process_page, url, base_url)
            pending.add(future)

            while pending:
                done = next(as_completed(pending))
                pending.discard(done)

                result = done.result()

                # External checks return None
                if result is None:
                    continue

                internal_urls, external_checks = result

                # Submit external link checks
                for source_url, target_url in external_checks:
                    pending.add(
                        executor.submit(self._check_external, source_url, target_url)
                    )

                # Submit new internal pages to crawl
                for source_url, new_url in internal_urls:
                    with self.lock:
                        if new_url not in self.visited:
                            self.visited.add(new_url)
                            pending.add(
                                executor.submit(
                                    self._process_page,
                                    new_url,
                                    base_url,
                                    source_url,
                                )
                            )
