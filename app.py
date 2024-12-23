from flask import Flask, request, render_template

from search_engine import search_db

app = Flask(__name__)

@app.route("/")
def start():
    return "<h1>Hello world.</h1><p>OK.</p>"

@app.route("/search")
def search():
    search_query = request.args.get("search_query", "")
    relevant_links = search_db(search_query) if search_query else ""
    return render_template("search.html", search_query=search_query, relevant_links=relevant_links)
