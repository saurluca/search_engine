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
    
    if q:
        start_time = time()
        results = search_db(q)
        search_time = round(time() - start_time, 2)
        result_count = len(results)
        
        # Debug print
        print(f"Query: {q}")
        print(f"Found {result_count} results")
        print(f"First result: {results[0] if results else 'None'}")
    else:
        results = []
        search_time = 0
        result_count = 0
        
    return render_template(
        "search.html",
        q=q,
        results=results,
        search_time=search_time,
        result_count=result_count
    )

@app.route("/debug/search")
def debug_search():
    """Debug endpoint that returns raw JSON search results."""
    q = request.args.get("q", "").strip()
    if q:
        results = search_db(q)
        return jsonify({
            'query': q,
            'count': len(results),
            'results': results
        })
    return jsonify({'error': 'No query provided'})