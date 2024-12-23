import requests
from bs4 import BeautifulSoup
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir



prefix = "https://vm009.rz.uos.de/crawl/"

start_url = prefix+'index.html'

visited = set()
agenda = [start_url]

schema = Schema(title=TEXT(stored=True), content=TEXT)
index_dir = "index"


def print_all_woosh_entries():
    print("all")
    # Open the index
    ix = open_dir(index_dir)

    # Extract all saved text from the index
    with ix.searcher() as searcher:
        all_text = []
        for docnum in range(searcher.doc_count()):
            doc = searcher.stored_fields(docnum)  # Get stored fields for the document
            for key, value in doc.items():
                if isinstance(value, str):  # Ensure the value is text
                    all_text.append(value)

    # Combine all text into a single string (optional)
    combined_text = "\n".join(all_text)

    # Output the text
    print(combined_text)


def is_same_domain(url):
    return url.startswith(prefix)


def resolve_url(base_url, link):
    """
    Manually resolve relative URLs.
    """
    if link.startswith('http://') or link.startswith('https://'):
        return link  # Absolute URL
    if link.startswith('/'):
        return prefix + link[1:]  # Root-relative URL
    return base_url.rsplit('/', 1)[0] + '/' + link  # Page-relative URL


def get_new_links(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True)]
            print("Found links:", links)

            for link in links:
                full_link = resolve_url(url, link)
                if is_same_domain(full_link) and full_link not in visited and full_link not in agenda:
                    agenda.append(full_link)
        else:
            print("HTTP Error:", r.status_code)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)


def get_text(url, writer):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            text = soup.find('body').text
            writer.add_document(title=url, content=text)
        else:
            print("HTTP Error:", r.status_code)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)


def crawl_page(url, writer):
    print("Crawling:", url)
    get_new_links(url)
    get_text(url, writer)


def run():
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    while agenda:
        url = agenda.pop()
        if url not in visited:
            visited.add(url)
            crawl_page(url, writer)

    writer.commit()

    print("Crawling complete. Total pages visited:", len(visited))
    print("All links visited:", visited)


if __name__ == '__main__':
    run()
    print_all_woosh_entries()

