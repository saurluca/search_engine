"""
Search Engine Module with advanced search capabilities using Whoosh.
"""

import re
from pathlib import Path
from typing import Dict, List

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin


class SearchEngine:
    """Search engine implementation using Whoosh."""
    
    def __init__(self, index_dir: str = "search_index"):
        """
        Initialize the search engine.
        
        Args:
            index_dir: Directory to store the search index
        """
        self.index_dir = Path(index_dir)
        self.analyzer = StemmingAnalyzer()
        
        # Define schema with stemming analyzer for better matching
        self.schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True, analyzer=self.analyzer, field_boost=2.0),
            content=TEXT(stored=True, analyzer=self.analyzer)
        )
        
        # Create or open index
        self._init_index()

    def _init_index(self) -> None:
        """Initialize or open the search index."""
        if not self.index_dir.exists():
            self.index_dir.mkdir()
            self.index = create_in(self.index_dir, self.schema)
        else:
            self.index = open_dir(self.index_dir)

    def add_page(self, url: str, title: str, content: str) -> None:
        """
        Add or update a page in the index.
        
        Args:
            url: Page URL
            title: Page title
            content: Page content
        """
        writer = self.index.writer()

        try:
            writer.update_document(
                url=url,
                title=str(title or url),
                content=str(content)
            )
            writer.commit()
            print(f"Indexed page: {url}")
        except Exception as e:
            writer.cancel()
            print(f"Error indexing {url}: {e}")

    def get_excerpt_with_highlight(self, content: str, query: str, 
                                 context_chars: int = 200) -> str:
        """Generate a relevant excerpt with highlighted search terms."""
        content_lower = content.lower()
        query_terms = query.lower().split()
        
        # Find the first occurrence of any query term
        first_pos = len(content)
        first_term = None
        
        for term in query_terms:
            pos = content_lower.find(term)
            if pos != -1 and pos < first_pos:
                first_pos = pos
                first_term = term
        
        if first_pos == len(content):
            return content[:context_chars] + "..."
            
        # Calculate excerpt boundaries
        start = max(0, first_pos - context_chars // 2)
        end = min(len(content), first_pos + len(first_term) + context_chars // 2)
        
        # Get the excerpt
        excerpt = content[start:end]
        
        # Add ellipsis
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        
        # Escape HTML
        excerpt = excerpt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Highlight all query terms
        for term in query_terms:
            pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
            excerpt = pattern.sub(r'<mark>\1</mark>', excerpt)
        
        return excerpt

    def search(self, query: str, fuzzy: bool = True, 
               max_results: int = 20) -> List[Dict[str, str]]:
        """
        Search for pages matching the query.
        
        Args:
            query: Search query
            fuzzy: Enable fuzzy matching
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents with url, title, and highlighted excerpt
        """
        if not query.strip():
            return []
            
        with self.index.searcher() as searcher:
            # Configure query parser
            parser = MultifieldParser(["title", "content"], self.index.schema)
            
            if fuzzy:
                # Add fuzzy matching capability
                parser.add_plugin(FuzzyTermPlugin())
                # Convert terms to fuzzy terms with edit distance of 1
                query = ' '.join(f'{term}~1' for term in query.split())
            
            # Parse query
            q = parser.parse(query)
            
            # Search
            results = searcher.search(q, limit=max_results)
            
            # Format results
            formatted_results = []
            for hit in results:
                # Generate excerpt with highlighted terms
                excerpt = self.get_excerpt_with_highlight(
                    hit['content'], 
                    query
                )
                
                # Highlight title if it matches
                title = hit['title']
                for term in query.split():
                    pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
                    title = pattern.sub(r'<mark>\1</mark>', title)
                
                formatted_results.append({
                    'url': hit['url'],
                    'title': title,
                    'text': excerpt,
                    'score': hit.score
                })
            
            return formatted_results

# Global search engine instance
_search_engine = None

def init_search_engine():
    """Initialize the global search engine instance."""
    global _search_engine
    _search_engine = SearchEngine()

def add_page_to_db(url: str, title: str, content: str) -> None:
    """Add a page to the search index."""
    if _search_engine is None:
        init_search_engine()
    _search_engine.add_page(url, title, content)

def search_db(query: str) -> List[Dict[str, str]]:
    """Search for pages matching the query."""
    if _search_engine is None:
        init_search_engine()
    return _search_engine.search(query)

# Initialize search engine when module is imported
init_search_engine()
