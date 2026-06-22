import os
import math
from flask import Flask, render_template, request, jsonify

# Custom modules for loading, searching, sorting and analyzing the dataset
from data_loader import load_posts
from search import linear_search
from sorting import merge_sort, sort_by_date
from analytics import trending_hashtags
from creator_analytics import popular_creators
from statistics import get_statistics
from relevance import relevance_search

app = Flask(__name__)

# ---------------------------------------------------------------------
# Configuration & File Management
# ---------------------------------------------------------------------

# Safely configure the upload folder relative to the current file
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the directory exists so the app never crashes on boot
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global State Variables
posts = []
current_filename = None

# Memory cache to prevent re-sorting on page changes
cached_sorted_posts = []
current_sort_criteria = None

# ---------------------------------------------------------------------
# Dynamic Startup Check (Self-Healing Boot Sequence)
# ---------------------------------------------------------------------

# Scan the uploads folder for any existing dataset files
existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.txt')]

if existing_files:
    # Auto-load the first available text file
    current_filename = existing_files[0]
    filepath = os.path.join(UPLOAD_FOLDER, current_filename)
    
    try:
        posts = load_posts(filepath)
        print(f"🎒 Successfully auto-loaded dataset: {current_filename} ({len(posts)} posts)")
    except Exception as e:
        print(f"⚠️ Error loading existing file {current_filename}: {e}")
        # Reset memory to safe empty defaults if the file is corrupted
        posts = []
        current_filename = None
else:
    print("✨ No existing dataset found. Starting with a clean slate.")


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------

def get_paginated_list(results):
    page = request.args.get("page", 1, type=int)
    per_page = 15  # results per page

    total_items = len(results)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    return results[start:end], page, total_pages, total_items


def render_paginated(template, key, items):
    """Paginate `items` and render `template` with them passed as `key`.

    Every results/trending/creators route follows the same
    paginate-then-render shape, so this keeps that logic in one place.
    """
    paginated, page, total_pages, total_items = get_paginated_list(items)
    return render_template(template, page=page, total_pages=total_pages, **{key: paginated})


def remove_dataset_file(filename, log_label="Deleted file"):
    """Remove a dataset file from the uploads folder if it exists."""
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"🗑️ {log_label}: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to delete {filename}: {e}")


def reset_cache():
    """Clear the sorted-results cache so the next page view re-sorts."""
    global cached_sorted_posts, current_sort_criteria
    cached_sorted_posts = []
    current_sort_criteria = None


# ---------------------------------------------------------------------
# Application Routes
# ---------------------------------------------------------------------

@app.route("/")
def home():
    # Pass the current file state to the template
    return render_template("index.html", current_file=current_filename, record_count=len(posts))

@app.route("/sort/<criteria>")
def sort_posts(criteria):
    global cached_sorted_posts, current_sort_criteria

    # If the user selected a NEW filter, or our cache is empty, we must do the heavy sorting
    if criteria != current_sort_criteria or not cached_sorted_posts:
        print(f"🔄 Performing heavy sort for: {criteria}...")
        cached_sorted_posts = merge_sort(posts, criteria)
        current_sort_criteria = criteria
    else:
        # If the criteria is the same (they just changed pages), skip the sort entirely!
        print(f"⚡ Using constant-time cached data for: {criteria}")

    return render_paginated("results.html", "results", cached_sorted_posts)

@app.route("/recent")
def recent_posts():
    global cached_sorted_posts, current_sort_criteria

    # Treat "recent" as just another criteria string for the cache
    if current_sort_criteria != "recent" or not cached_sorted_posts:
        print("🔄 Performing heavy date sort...")
        cached_sorted_posts = sort_by_date(posts)
        current_sort_criteria = "recent"
    else:
        print("⚡ Using constant-time cached data for recent posts")

    return render_paginated("results.html", "results", cached_sorted_posts)

@app.route("/trending")
def trending():
    trends = trending_hashtags(posts)
    return render_paginated("trending.html", "trends", trends)

@app.route("/creators")
def creators():
    ranked_creators = popular_creators(posts)
    return render_paginated("creators.html", "creators", ranked_creators)

@app.route("/statistics")
def statistics():
    stats = get_statistics(posts)
    return render_template("statistics.html", stats=stats)

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")
    results = linear_search(posts, keyword)
    return render_paginated("results.html", "results", results)

@app.route("/relevance/<keyword>")
def relevance(keyword):
    results = relevance_search(posts, keyword)
    return render_paginated("results.html", "results", results)


# ---------------------------------------------------------------------
# File Management Routes (Upload & Delete)
# ---------------------------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload():
    global posts, current_filename

    file = request.files["dataset"]

    if file:
        # Replace any previously loaded dataset on disk
        if current_filename:
            remove_dataset_file(current_filename, "Replaced and deleted old file")

        # Save and load the new file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        posts = load_posts(filepath)
        current_filename = file.filename
        reset_cache()  # new data means cached sort results are stale

        return jsonify({
            "message": "Dataset Loaded Successfully!",
            "filename": current_filename,
            "count": len(posts)
        })

    return jsonify({"error": "Upload Failed"}), 400

@app.route("/delete", methods=["POST"])
def delete_dataset():
    global posts, current_filename

    # Remove the active file from disk, then wipe it from memory and cache
    if current_filename:
        remove_dataset_file(current_filename, "Physically deleted file from storage")

    posts = []
    current_filename = None
    reset_cache()

    return jsonify({"message": "Dataset cleared from memory and storage."})


if __name__ == "__main__":
    app.run(debug=True)