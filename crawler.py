"""
Web Crawler Module
"""

import logging
from typing import Set, List, Optional
from urllib.parse import urljoin, urlparse, urldefrag
import os
import shutil

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from search_engine import add_page_to_db, init_search_engine, _search_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebCrawler:
    """A web crawler that processes pages within a specified domain."""

    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.timeout = timeout
        self.visited: Set[str] = set()
        self.agenda: List[str] = [base_url]
        self.pages_stored = 0

    def _is_same_domain(self, url: str) -> bool:
        return url.startswith(self.base_url)

    def _clean_url(self, url: str) -> str:
        clean_url, _ = urldefrag(url)
        return clean_url

    def _resolve_url(self, current_url: str, link: str) -> str:
        absolute_url = urljoin(current_url, link)
        return self._clean_url(absolute_url)

    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None

    def _extract_links(self, url: str, soup: BeautifulSoup) -> None:
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        for link in links:
            full_link = self._resolve_url(url, link)
            if (self._is_same_domain(full_link) and 
                full_link not in self.visited and 
                full_link not in self.agenda):
                self.agenda.append(full_link)

    def _extract_and_store_content(self, url: str, soup: BeautifulSoup) -> None:
        """Extract and store page content."""
        try:
            # Extract title
            title = soup.title.string if soup.title else None
            if not title:
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else url

            # Clean up the content
            for tag in soup.find_all(['script', 'style']):
                tag.decompose()

            # Extract main content
            content = soup.get_text(separator=' ', strip=True)

            # Store the page
            if content:
                logger.info(f"Storing page: {url}")
                logger.info(f"Title: {title}")
                logger.info(f"Content length: {len(content)} characters")
                
                add_page_to_db(url, title, content)
                self.pages_stored += 1
                
                logger.info(f"Successfully stored page {self.pages_stored}")
            else:
                logger.warning(f"No content extracted from {url}")

        except Exception as e:
            logger.error(f"Error processing page {url}: {e}")

    def crawl_page(self, url: str) -> None:
        """Crawl a single page."""
        logger.info(f"Crawling: {url}")
        
        response = self._fetch_page(url)
        if not response:
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        self._extract_links(url, soup)
        self._extract_and_store_content(url, soup)

    def run(self) -> None:
        """Execute the crawling process."""
        logger.info("Starting crawler...")
        
        while self.agenda:
            url = self.agenda.pop()
            clean_url = self._clean_url(url)
            if clean_url not in self.visited:
                self.visited.add(clean_url)
                self.crawl_page(clean_url)

        logger.info(f"Crawling complete. Pages visited: {len(self.visited)}")
        logger.info(f"Pages stored: {self.pages_stored}")


def main():
    """Main entry point for the crawler."""
    # Clear existing index
    index_dir = "search_index"
    if os.path.exists(index_dir):
        print(f"Removing existing index at {index_dir}")
        shutil.rmtree(index_dir)
    
    # Reinitialize search engine
    print("Initializing fresh search index...")
    init_search_engine()
    
    # Configuration
    BASE_URL = "https://whoosh.readthedocs.io/en/latest/"
    
    print("Starting crawler...")
    
    # Initialize and run crawler
    crawler = WebCrawler(BASE_URL)
    crawler.run()
    
    # Print index statistics
    print("\nIndexing completed:")
    with _search_engine.index.searcher() as searcher:
        doc_count = searcher.doc_count()
        print(f"Documents indexed: {doc_count}")


if __name__ == '__main__':
    main()
