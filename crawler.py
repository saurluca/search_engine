import requests
from bs4 import BeautifulSoup

prefix = "https://vm009.rz.uos.de/crawl/"

start_url = prefix+'index.html'

agenda = [start_url]

def get_new_links(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        agenda.extend(links)
    else:
        print("Error")


def crawl_page(url):
    get_new_links(url)


def run():
    while agenda:
       crawl_page(agenda.pop())


if __name__ == '__main__':
    run()