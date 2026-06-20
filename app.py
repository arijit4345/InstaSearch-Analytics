from flask import Flask, render_template, request, jsonify
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
import math

from hashmap_search import (
    build_creator_index,
    build_hashtag_index,
    creator_search,
    hashtag_search
)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
current_filename = "dataset.txt" # Tracks the default file on startup

posts = []
posts = load_posts("dataset.txt")

creator_index = build_creator_index(posts)

hashtag_index = build_hashtag_index(posts)

@app.route("/")
def home():
    # Pass the current file state to the template
    return render_template("index.html", current_file=current_filename, record_count=len(posts))

def get_paginated_list(results):
    page = request.args.get("page", 1, type=int)
    per_page = 15 # Change this to 10 or 20 if you prefer

    total_items = len(results)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    return results[start:end], page, total_pages, total_items

@app.route("/creator/<name>")
def search_creator(name):
    results = creator_search(creator_index, name)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/hashtag/<tag>")
def search_hashtag(tag):
    results = hashtag_search(hashtag_index, tag)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/sort/<criteria>")
def sort_posts(criteria):
    sorted_posts = merge_sort(posts, criteria)
    paginated, page, total_pages, total_items = get_paginated_list(sorted_posts)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/trending")
def trending():
    trends = trending_hashtags(posts)
    paginated, page, total_pages, total_items = get_paginated_list(trends)
    
    return render_template(
        "trending.html",
        trends=paginated,
        page=page,
        total_pages=total_pages
    )

@app.route("/creators")
def creators():
    ranked_creators = popular_creators(posts)
    paginated, page, total_pages, total_items = get_paginated_list(ranked_creators)
    
    return render_template(
        "creators.html",
        creators=paginated,
        page=page,
        total_pages=total_pages
    )

@app.route("/statistics")
def statistics():

    stats = get_statistics(posts)

    return render_template(
        "statistics.html",
        stats=stats
    )

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")
    results = linear_search(posts, keyword)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/upload", methods=["POST"])
def upload():
    global posts, creator_index, hashtag_index, current_filename # Add current_filename here

    file = request.files["dataset"]

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        
        posts = load_posts(filepath)
        creator_index = build_creator_index(posts)
        hashtag_index = build_hashtag_index(posts)
        current_filename = file.filename # Save the name

        # Return JSON so the frontend can update the UI dynamically
        return jsonify({
            "message": "Dataset Loaded Successfully!",
            "filename": current_filename,
            "count": len(posts)
        })

    return jsonify({"error": "Upload Failed"}), 400

@app.route("/delete", methods=["POST"])
def delete_dataset():
    global posts, creator_index, hashtag_index, current_filename

    # Wipe everything from memory
    posts = []
    creator_index = {}
    hashtag_index = {}
    current_filename = None

    return jsonify({"message": "Dataset cleared."})

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
    paginated, page, total_pages, total_items = get_paginated_list(recent)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/relevance/<keyword>")
def relevance(keyword):
    results = relevance_search(posts, keyword)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)