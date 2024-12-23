from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def start():
    return "<h1>Hello world.</h1><p>OK.</p>"

@app.route("/search")
def search():
    search_query = request.args.get("search_query", "")
    return render_template("search.html", search_query=search_query)
