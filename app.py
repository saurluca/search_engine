from flask import Flask, request, render_template, jsonify
from time import time
from search_engine import search_db

app = Flask(__name__)

@app.route("/")
def start():
    return render_template("index.html")

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    fuzzy = True
    
    if q:
        start_time = time()
        results = search_db(q)  # Fuzzy search is enabled by default
        search_time = round(time() - start_time, 2)
        result_count = len(results)
    else:
        results = []
        search_time = 0
        result_count = 0
        
    return render_template(
        "search.html",
        q=q,
        results=results,
        search_time=search_time,
        result_count=result_count,
        fuzzy=fuzzy
    )
