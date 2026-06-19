from flask import Flask, render_template, request
from data_loader import load_posts
from search import linear_search

app = Flask(__name__)

posts = load_posts("dataset.txt")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():

    keyword = request.form["query"]

    results = linear_search(posts, keyword)

    return render_template(
        "results.html",
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)