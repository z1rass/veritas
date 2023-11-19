from flask import Flask, url_for, request

app = Flask(__name__)


@app.route('/<name>')
def name(name):
    return f"helllo {name}"

app.run(debug=True)

