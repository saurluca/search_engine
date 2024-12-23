import os

from whoosh.fields import Schema, TEXT
from whoosh.index import open_dir, create_in
from whoosh.qparser import QueryParser


schema = Schema(link=TEXT(stored=True), content=TEXT(stored=True))
index_dir = "index"


def search(search_query):
    # Todo improve error handling
    if not search_query:
        return "no query"

    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(search_query)
        results = searcher.search(query)
        print("results: ")
        relevant_links = []
        for r in results:
            print(r['link'])
            relevant_links.append(r["link"])
        return relevant_links


def add_page_to_db(url, text):
    # Todo add error handling
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        ix = create_in(index_dir, schema)
    else:
        ix = open_dir(index_dir)
    try:
        writer = ix.writer()
        writer.add_document(link=url, content=text)
        writer.commit()
    except Exception as e:
        print(f"Failed to add document: {e}")


def print_all_woosh_entries():
    print("All entries from Whoosh index (Link and Content):")
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        for docnum in range(searcher.doc_count()):
            doc = searcher.stored_fields(docnum)
            link = doc.get('link', 'No link')
            content = doc.get('content', 'No content')
            print(f"Link: {link}\nContent: {content}\n{'-'*40}")


def test_search(search_query):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(search_query)
        results = searcher.search(query)
        print("results: ")
        for r in results:
            print(r['link'])
