from unittest.mock import MagicMock, patch

import requests
from bs4 import BeautifulSoup

from http_scrapper.crawler import Crawler


class TestIsSameDomain:
    def test_same_domain(self):
        crawler = Crawler()
        assert crawler.is_same_domain(
            "https://example.com/page1", "https://example.com/page2"
        )

    def test_different_domain(self):
        crawler = Crawler()
        assert not crawler.is_same_domain("https://example.com", "https://other.com")

    def test_subdomain_differs(self):
        crawler = Crawler()
        assert not crawler.is_same_domain(
            "https://www.example.com", "https://api.example.com"
        )


class TestExtractLinksAndResources:
    def test_extracts_anchor_links(self):
        crawler = Crawler()
        html = '<html><body><a href="/page2">Link</a></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        links = crawler.extract_links_and_resources(soup, "https://example.com/page1")
        assert "https://example.com/page2" in links

    def test_extracts_img_src(self):
        crawler = Crawler()
        html = '<html><body><img src="/img/photo.jpg"></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        links = crawler.extract_links_and_resources(soup, "https://example.com/")
        assert "https://example.com/img/photo.jpg" in links

    def test_extracts_script_src(self):
        crawler = Crawler()
        html = '<html><body><script src="/js/app.js"></script></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        links = crawler.extract_links_and_resources(soup, "https://example.com/")
        assert "https://example.com/js/app.js" in links

    def test_removes_fragments(self):
        crawler = Crawler()
        html = '<html><body><a href="/page#section">Link</a></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        links = crawler.extract_links_and_resources(soup, "https://example.com/")
        assert "https://example.com/page" in links
        assert not any("#" in link for link in links)

    def test_skips_empty_href(self):
        crawler = Crawler()
        html = "<html><body><a>No href</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        links = crawler.extract_links_and_resources(soup, "https://example.com/")
        assert len(links) == 0


class TestCrawl:
    @patch("http_scrapper.crawler.requests.get")
    def test_crawl_records_http_links(self, mock_get):
        html = '<html><body><a href="http://insecure.com/page">Link</a></body></html>'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = Crawler()
        crawler.crawl("https://example.com", "https://example.com")

        assert len(crawler.http_links) == 1
        assert crawler.http_links[0] == (
            "https://example.com",
            "http://insecure.com/page",
        )

    @patch("http_scrapper.crawler.requests.get")
    def test_crawl_skips_visited(self, mock_get):
        html = "<html><body></body></html>"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = Crawler()
        crawler.crawl("https://example.com", "https://example.com")
        crawler.crawl("https://example.com", "https://example.com")

        assert crawler.page_counter == 1

    @patch("http_scrapper.crawler.requests.get")
    def test_crawl_records_404_links(self, mock_get):
        html = '<html><body><a href="https://example.com/broken">Link</a></body></html>'

        def side_effect(url, timeout=5):
            resp = MagicMock()
            if url == "https://example.com/broken":
                resp.raise_for_status.side_effect = requests.RequestException("404")
            else:
                resp.status_code = 200
                resp.text = html
                resp.raise_for_status = MagicMock()
            return resp

        mock_get.side_effect = side_effect

        crawler = Crawler()
        crawler.crawl("https://example.com", "https://example.com")

        assert len(crawler.links_404) == 1
        assert crawler.links_404[0] == (
            "https://example.com",
            "https://example.com/broken",
        )
