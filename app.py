import os
import math
from flask import Flask, render_template, request, jsonify

# Import custom modules (Linear search retained per your request)
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
    per_page = 15 # Change this to 10 or 20 if you prefer

    total_items = len(results)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    return results[start:end], page, total_pages, total_items


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

    paginated, page, total_pages, total_items = get_paginated_list(cached_sorted_posts)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

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

    paginated, page, total_pages, total_items = get_paginated_list(cached_sorted_posts)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/trending")
def trending():
    trends = trending_hashtags(posts)
    paginated, page, total_pages, total_items = get_paginated_list(trends)
    return render_template("trending.html", trends=paginated, page=page, total_pages=total_pages)

@app.route("/creators")
def creators():
    ranked_creators = popular_creators(posts)
    paginated, page, total_pages, total_items = get_paginated_list(ranked_creators)
    return render_template("creators.html", creators=paginated, page=page, total_pages=total_pages)

@app.route("/statistics")
def statistics():
    stats = get_statistics(posts)
    return render_template("statistics.html", stats=stats)

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")
    results = linear_search(posts, keyword)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)

@app.route("/relevance/<keyword>")
def relevance(keyword):
    results = relevance_search(posts, keyword)
    paginated, page, total_pages, total_items = get_paginated_list(results)
    return render_template("results.html", results=paginated, page=page, total_pages=total_pages)


# ---------------------------------------------------------------------
# File Management Routes (Upload & Delete)
# ---------------------------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload():
    global posts, current_filename, cached_sorted_posts, current_sort_criteria

    file = request.files["dataset"]

    if file:
        # 1. CLEANUP PREVIOUS FILE
        if current_filename:
            old_filepath = os.path.join(app.config["UPLOAD_FOLDER"], current_filename)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                    print(f"🗑️ Replaced and deleted old file: {current_filename}")
                except Exception as e:
                    print(f"⚠️ Failed to delete old file: {e}")

        # 2. SAVE THE NEW FILE
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        
        # 3. LOAD NEW DATA & RESET CACHE
        posts = load_posts(filepath)
        current_filename = file.filename
        cached_sorted_posts = []       # Reset cache so new data shows up
        current_sort_criteria = None   # Reset cache criteria

        return jsonify({
            "message": "Dataset Loaded Successfully!",
            "filename": current_filename,
            "count": len(posts)
        })

    return jsonify({"error": "Upload Failed"}), 400

@app.route("/delete", methods=["POST"])
def delete_dataset():
    global posts, current_filename, cached_sorted_posts, current_sort_criteria

    # 1. Physically delete the active file from the server's hard drive
    if current_filename:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], current_filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Physically deleted file from storage: {current_filename}")
            except Exception as e:
                print(f"⚠️ Failed to physically delete file: {e}")

    # 2. Wipe the application memory & caches entirely
    posts = []
    current_filename = None
    cached_sorted_posts = []       # Clear the cache!
    current_sort_criteria = None   # Clear the cache!

    return jsonify({"message": "Dataset cleared from memory and storage."})


if __name__ == "__main__":
    app.run(debug=True)