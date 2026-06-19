from flask import Flask, render_template, request
from data_loader import load_posts
from search import linear_search

from hashmap_search import (
    build_creator_index,
    build_hashtag_index,
    creator_search,
    hashtag_search
)

app = Flask(__name__)

posts = load_posts("dataset.txt")

creator_index = build_creator_index(posts)

hashtag_index = build_hashtag_index(posts)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/creator/<name>")
def search_creator(name):

    results = creator_search(
        creator_index,
        name
    )

    return render_template(
        "results.html",
        results=results
    )

@app.route("/hashtag/<tag>")
def search_hashtag(tag):

    results = hashtag_search(
        hashtag_index,
        tag
    )

    return render_template(
        "results.html",
        results=results
    )

def search():

    keyword = request.form["query"]

    results = linear_search(posts, keyword)

    return render_template(
        "results.html",
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)