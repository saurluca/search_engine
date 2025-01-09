# search_engine.py
"""
Search Engine Module

Handles storage and retrieval of web page content with search capabilities.
"""

from typing import Dict, List
import sqlite3
import os

def get_db_path():
    """Get absolute path to the database file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'search_index.sqlite3')

def init_db(force: bool = False):
    """
    Initialize the database with required tables.
    
    Args:
        force: If True, recreate the tables even if they exist
    """
    db_path = get_db_path()
    print(f"Initializing database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        if force:
            c.execute('DROP TABLE IF EXISTS pages')
            print("Dropped existing tables")
            
        # Create table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Database initialized successfully")
        
        # Verify table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pages'")
        if c.fetchone():
            print("Verified 'pages' table exists")
        else:
            print("ERROR: Table creation failed!")
            
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

def add_page_to_db(url: str, title: str, content: str) -> bool:
    """
    Add or update a page in the database.
    
    Args:
        url: Page URL
        title: Page title
        content: Page content text
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not url or not content:
        print(f"Skipping invalid page: URL={url}, Title={title}, Content length={len(content) if content else 0}")
        return False

    # Ensure database and table exist
    init_db()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        print(f"\nStoring page: {url}")
        print(f"Title length: {len(title)} characters")
        print(f"Content length: {len(content)} characters")
        
        c.execute(
            'INSERT OR REPLACE INTO pages (url, title, content) VALUES (?, ?, ?)',
            (url, title or url, content)
        )
        conn.commit()
        
        # Verify the insertion
        c.execute('SELECT COUNT(*) FROM pages WHERE url = ?', (url,))
        count = c.fetchone()[0]
        success = count > 0
        print(f"Page {'stored successfully' if success else 'failed to store'}")
        return success
        
    except sqlite3.Error as e:
        print(f"Database error while storing page {url}: {e}")
        return False
    finally:
        conn.close()

def search_db(query: str) -> List[Dict[str, str]]:
    """
    Search for pages containing the query.
    """
    if not query.strip():
        return []
    
    # Ensure database and table exist
    init_db()
    
    db_path = get_db_path()
    print(f"\nSearching database at: {db_path}")
    print(f"Query: {query}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check if we have any data
        c.execute('SELECT COUNT(*) FROM pages')
        total_pages = c.fetchone()[0]
        print(f"Total pages in database: {total_pages}")
        
        if total_pages == 0:
            print("Database is empty!")
            return []
        
        # Perform the search
        search_term = f"%{query}%"
        c.execute('''
            SELECT url, title, content 
            FROM pages 
            WHERE 
                lower(content) LIKE lower(?) 
                OR lower(title) LIKE lower(?)
        ''', (search_term, search_term))
        
        results = []
        rows = c.fetchall()
        print(f"Found {len(rows)} matching pages")
        
        for row in rows:
            url, title, content = row
            results.append({
                'url': url,
                'title': title,
                'text': content[:200] + "..." if len(content) > 200 else content
            })
            print(f"\nMatch: {url}")
            print(f"Title: {title}")
        
        return results
        
    except sqlite3.Error as e:
        print(f"Database error during search: {e}")
        return []
    finally:
        conn.close()

def debug_db():
    """Print database contents for debugging."""
    # Ensure database and table exist
    init_db()
    
    db_path = get_db_path()
    print(f"\nDebug: Database at {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check table structure
        c.execute("PRAGMA table_info(pages)")
        print("\nTable structure:")
        for col in c.fetchall():
            print(col)
            
        # Check content
        c.execute('SELECT COUNT(*) FROM pages')
        count = c.fetchone()[0]
        print(f"\nTotal pages: {count}")
        
        if count > 0:
            print("\nFirst few entries:")
            c.execute('SELECT url, title, substr(content, 1, 100) FROM pages LIMIT 3')
            for row in c.fetchall():
                print(f"\nURL: {row[0]}")
                print(f"Title: {row[1]}")
                print(f"Content preview: {row[2]}...")
    
    except sqlite3.Error as e:
        print(f"Debug error: {e}")
    finally:
        conn.close()
