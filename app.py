import os
import math
from flask import Flask, render_template, request, jsonify

from data_loader import load_posts
from search import linear_search
from sorting import merge_sort, sort_by_date
from analytics import trending_hashtags
from creator_analytics import popular_creators
from statistics import get_statistics
from relevance import relevance_search

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

posts = []
current_filename = None

# Unified Cache for Stateful Explore
cached_sorted_posts = []
current_explore_state = None 

existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.txt')]
if existing_files:
    current_filename = existing_files[0]
    filepath = os.path.join(UPLOAD_FOLDER, current_filename)
    try:
        posts = load_posts(filepath)
        print(f"🎒 Auto-loaded dataset: {current_filename}")
    except Exception as e:
        posts = []
        current_filename = None

def get_paginated_list(results):
    page = request.args.get("page", 1, type=int)
    per_page = 15
    total_items = len(results)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end], page, total_pages, total_items

@app.route("/")
def home():
    return render_template("index.html", current_file=current_filename, record_count=len(posts))

# --- THE NEW MASTER ROUTE ---
@app.route("/explore", methods=["GET"])
def explore():
    global cached_sorted_posts, current_explore_state

    # 1. Capture the exact state from the URL
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date") # Default to recent posts
    order = request.args.get("order", "desc")  # Default to highest/newest first

    # 2. Build a unique string to check our cache
    state_key = f"{search_query}|{sort_by}|{order}"

    # 3. If the state changed (they searched, sorted, or flipped direction), run the math!
    if state_key != current_explore_state or not cached_sorted_posts:
        print(f"🔄 Processing new explore state: {state_key}")
        
        filtered_posts = posts
        
        # A. Filter by Search first (if any)
        if search_query:
            filtered_posts = linear_search(filtered_posts, search_query)
            
        # B. Sort the remaining results
        if sort_by == "date":
            filtered_posts = sort_by_date(filtered_posts) # Returns desc naturally
        else:
            filtered_posts = merge_sort(filtered_posts, sort_by) # Returns desc naturally
            
        # C. Reverse for Ascending order
        if order == "asc":
            filtered_posts = filtered_posts[::-1]
            
        # Save to memory
        cached_sorted_posts = filtered_posts
        current_explore_state = state_key
    else:
        print(f"⚡ Using constant-time cache for: {state_key}")

    paginated, page, total_pages, total_items = get_paginated_list(cached_sorted_posts)
    
    return render_template(
        "results.html", 
        results=paginated, 
        page=page, 
        total_pages=total_pages,
        total_items=total_items,
        current_search=search_query,
        current_sort=sort_by,
        current_order=order
    )

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

@app.route("/upload", methods=["POST"])
def upload():
    global posts, current_filename, cached_sorted_posts, current_explore_state
    file = request.files["dataset"]
    if file:
        if current_filename:
            old_filepath = os.path.join(app.config["UPLOAD_FOLDER"], current_filename)
            if os.path.exists(old_filepath):
                try: os.remove(old_filepath)
                except Exception: pass

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        
        posts = load_posts(filepath)
        current_filename = file.filename
        cached_sorted_posts = []       
        current_explore_state = None   

        return jsonify({
            "message": "Dataset Loaded Successfully!",
            "filename": current_filename,
            "count": len(posts)
        })
    return jsonify({"error": "Upload Failed"}), 400

@app.route("/delete", methods=["POST"])
def delete_dataset():
    global posts, current_filename, cached_sorted_posts, current_explore_state
    if current_filename:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], current_filename)
        if os.path.exists(filepath):
            try: os.remove(filepath)
            except Exception: pass
    posts = []
    current_filename = None
    cached_sorted_posts = []       
    current_explore_state = None   
    return jsonify({"message": "Dataset cleared from memory and storage."})

if __name__ == "__main__":
    # Setting host='0.0.0.0' makes the server accessible via your local network IP
    app.run(host="0.0.0.0", port=5000, debug=True)