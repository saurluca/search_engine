from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def start():
    return "<form action='reversed' method='get'><input name='rev'></input></form>"

@app.route("/reversed")
def reversed():
    return f"<h1>{request.args['rev'][::-1]}</h1>"
