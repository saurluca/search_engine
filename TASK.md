# Seminar: Artificial Intelligence and the Web - Vips

## Task 2: Build a search engine

### **Build a search engine with all four components:**

- Crawler _(must run independently from search!)_
- Index
- Query parser and search algorithm
- User Frontend

Demonstrate it by crawling one website and making its content available to the user via a web frontend with a simple search form.

Make the result available on the provided demo server.

Submit the code and the link to the demo deployment.

### Grading criteria:

- Does the solution cover all requirements from the project description? (5/5)
- Is the solution deployed correctly? (2/2)
- Is the solution properly documented? (Code comments + README file) (1/1)
- Does the solution include additional creative ideas (one search engine extra, one UI improvement, e.g., nice design, usability improvements) (2/2)

### **Suggested order of building:**

**Week 1 of project:**

- Create a working environment on your computers
- Create a repository (Gitlab, GitHub, …) for your project 2 and make sure all group members can access it
- Start with adding a .gitignore and a requirements.txt file to the repository (requirements are requests and beautifulsoup4)
- Create a `crawler.py` file and define the skeleton of the crawling algorithm:
  - Crawl (=get and parse) all HTML pages on a certain server
  - That can directly or indirectly be reached from a start URL
  - By following links on the pages.
  - Do not follow links to URLs on other servers and only process HTML responses.
  - Test the crawler with a simple website, e.g., [https://vm009.rz.uos.de/crawl/index.html](https://vm009.rz.uos.de/crawl/index.html)
- Build an in-memory index from the HTML text content found.
  - The most straightforward index is a dictionary with words as keys and lists of URLs that refer to pages that include the word.
- Add a function `search` that takes a list of words as a parameter and returns (by using the index) a list of links to all pages that contain all the words from the list.
- Test the functionality.

Don't worry if you don't get that far! Use the element chat and the Friday session to ask questions, report problems and tell about hurdles and obstacles!

**Week 2:**

- Replace the simple index with code using the woosh library ([https://whoosh.readthedocs.io/en/latest/intro.html](https://whoosh.readthedocs.io/en/latest/intro.html) ).
- Build a flask app (will be introduced in week 6) with two URLs that show the following behavior:
  - GET home URL: Show search form
  - GET search URL with parameter q: Search for q using the index and display a list of URLs as links

**Week 3:**

- Improve the index by adding information
- Improve the output by including title and teaser text
- Install your search engine on the demo server provided

# What to hand in

**1. Please provide:**

1.  Source code - either as a public github url (or invite tthelen to your private repository) or ZIP upload for this Vips task
2.  The URL of your deployment

**2. Who did what?**

If you didn't contribute equally to your project, please describe who did what (in max 2 short sentences per contributor)

Zeitraum: 21.11.2024, 21:00 – 10.01.2025, 18:00
