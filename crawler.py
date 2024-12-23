import requests
from bs4 import BeautifulSoup

from search_engine import add_page_to_db, search


prefix = "https://vm009.rz.uos.de/crawl/"
# prefix = "https://whoosh.readthedocs.io/en/latest/"

start_url = prefix+'index.html'
# start_url = prefix+"quickstart.html"

visited = set()
agenda = [start_url]


def is_same_domain(url):
    return url.startswith(prefix)


def resolve_url(base_url, link):
    # Manually resolve relative URLs.
    if link.startswith('http://') or link.startswith('https://'):
        return link  # Absolute URL
    if link.startswith('/'):
        return prefix + link[1:]  # Root-relative URL
    return base_url.rsplit('/', 1)[0] + '/' + link  # Page-relative URL


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


def get_text(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            text = soup.find('body').get_text(separator=' ', strip=True)
            text = str(text)
            add_page_to_db(url, text)
        else:
            print("HTTP Error:", r.status_code)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)


def crawl_page(url):
    print("Crawling:", url)
    get_new_links(url)
    get_text(url)


def run():
    while agenda:
        url = agenda.pop()
        if url not in visited:
            visited.add(url)
            crawl_page(url)

    print("Crawling complete. Total pages visited:", len(visited))
    print("All links visited:", visited)


if __name__ == '__main__':
    # run()
    search("egg")
