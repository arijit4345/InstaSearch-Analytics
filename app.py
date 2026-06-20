from flask import Flask, render_template, request
from data_loader import load_posts
from search import linear_search
from sorting import merge_sort
from analytics import trending_hashtags
from creator_analytics import popular_creators
from statistics import get_statistics
from performance import compare_search
from sorting import merge_sort, sort_by_date
from relevance import relevance_search
import os

from hashmap_search import (
    build_creator_index,
    build_hashtag_index,
    creator_search,
    hashtag_search
)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

posts = []
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

@app.route("/sort/<criteria>")
def sort_posts(criteria):

    sorted_posts = merge_sort(
        posts,
        criteria
    )

    return render_template(
        "results.html",
        results=sorted_posts
    )

@app.route("/trending")
def trending():

    trends = trending_hashtags(posts)

    return render_template(
        "trending.html",
        trends=trends
    )

@app.route("/creators")
def creators():

    ranked_creators = popular_creators(posts)

    return render_template(
        "creators.html",
        creators=ranked_creators
    )

@app.route("/statistics")
def statistics():

    stats = get_statistics(posts)

    return render_template(
        "statistics.html",
        stats=stats
    )

@app.route("/search", methods=["POST"])
def search():

    keyword = request.form["keyword"]

    results = linear_search(posts, keyword)

    return render_template(
        "results.html",
        results=results
    )

@app.route("/upload", methods=["POST"])
def upload():

    global posts
    global creator_index
    global hashtag_index

    file = request.files["dataset"]

    if file:

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        posts = load_posts(filepath)

        creator_index = build_creator_index(posts)

        hashtag_index = build_hashtag_index(posts)

        return f"Dataset Loaded Successfully! Total Posts: {len(posts)}"

    return "Upload Failed"

@app.route("/performance")
def performance():

    result = compare_search(
        posts,
        creator_index
    )

    return render_template(
        "performance.html",
        result=result
    )

@app.route("/recent")
def recent_posts():

    recent = sort_by_date(posts)

    return render_template(
        "results.html",
        results=recent
    )

@app.route("/relevance/<keyword>")
def relevance(keyword):

    results = relevance_search(
        posts,
        keyword
    )

    return render_template(
        "results.html",
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)