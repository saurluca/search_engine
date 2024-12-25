from flask import Flask, request, render_template

from search_engine import search_db

app = Flask(__name__)

@app.route("/")
def start():
    return "<h1>Hello world.</h1><p>OK.</p>"

@app.route("/search")
def search():
    q = request.args.get("q", "")
    relevant_links = search_db(q) if q else ""
    return render_template("search.html", q=q, relevant_links=relevant_links)
