import os
import math
import uuid
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename

from data_loader import load_posts
from search import linear_search
from sorting import merge_sort, sort_by_date
from analytics import trending_hashtags
from creator_analytics import popular_creators
from statistics import get_statistics
from relevance import relevance_search

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "instasearch-dev-session-key")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

datasets_by_session = {}

def get_session_id():
    if "dataset_session_id" not in session:
        session["dataset_session_id"] = uuid.uuid4().hex
    return session["dataset_session_id"]


def get_dataset_state():
    session_id = get_session_id()
    if session_id not in datasets_by_session:
        datasets_by_session[session_id] = {
            "posts": [],
            "filename": None,
            "cached_sorted_posts": [],
            "current_explore_state": None,
        }
    return datasets_by_session[session_id]


def clear_explore_cache(dataset_state):
    dataset_state["cached_sorted_posts"] = []
    dataset_state["current_explore_state"] = None


def get_paginated_list(results):
    page = request.args.get("page", 1, type=int)
    per_page = 15
    total_items = len(results)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end], page, total_pages, total_items


@app.route("/")
def home():
    dataset_state = get_dataset_state()
    posts = dataset_state["posts"]
    return render_template(
        "index.html",
        current_file=dataset_state["filename"],
        record_count=len(posts)
    )


@app.route("/explore", methods=["GET"])
def explore():
    dataset_state = get_dataset_state()
    posts = dataset_state["posts"]

    # 1. Capture state from URL (Original text string)
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    # 2. Parse the search string into UI Tokens (Chips) exactly how you requested
    ui_chips = []
    if search_query:
        tokens = search_query.split()
        creator_token = None
        hashtag_tokens = []
        text_tokens = []

        for t in tokens:
            if t.startswith("@") and not creator_token:
                creator_token = t
            elif t.startswith("#"):
                hashtag_tokens.append(t)
            else:
                text_tokens.append(t)

        # Build the visual list (Creator -> Text -> Hashtags)
        if creator_token:
            ui_chips.append({"type": "creator", "label": creator_token.replace("_", " "), "raw": creator_token})
        if text_tokens:
            text_raw = " ".join(text_tokens)
            ui_chips.append(
                {"type": "text", "label": text_raw, "raw": text_raw})
        for h in hashtag_tokens:
            ui_chips.append({"type": "hashtag", "label": h, "raw": h})

    # 3. Build a unique string to check our cache
    state_key = f"{search_query}|{sort_by}|{order}"

    # 4. If the state changed, run the math!
    if state_key != dataset_state["current_explore_state"] or not dataset_state["cached_sorted_posts"]:
        print(f"🔄 Processing new explore state: {state_key}")

        filtered_posts = posts

        # A. Filter by the Search logic
        if search_query:
            filtered_posts = linear_search(filtered_posts, search_query)

        # B. Sort the remaining results
        if sort_by == "date":
            filtered_posts = sort_by_date(filtered_posts)
        else:
            filtered_posts = merge_sort(filtered_posts, sort_by)

        # C. Reverse for Ascending order
        if order == "asc":
            filtered_posts = filtered_posts[::-1]

        # Save to memory
        dataset_state["cached_sorted_posts"] = filtered_posts
        dataset_state["current_explore_state"] = state_key
    else:
        print(f"⚡ Using constant-time cache for: {state_key}")

    paginated, page, total_pages, total_items = get_paginated_list(
        dataset_state["cached_sorted_posts"])

    return render_template(
        "results.html",
        results=paginated,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        current_search=search_query,
        ui_chips=ui_chips,          # Passing the tokens to the frontend
        current_sort=sort_by,
        current_order=order
    )


@app.route("/trending")
def trending():
    dataset_state = get_dataset_state()
    posts = dataset_state["posts"]
    trends = trending_hashtags(posts)
    paginated, page, total_pages, total_items = get_paginated_list(trends)
    return render_template("trending.html", trends=paginated, page=page, total_pages=total_pages)


@app.route("/creators")
def creators():
    dataset_state = get_dataset_state()
    posts = dataset_state["posts"]
    ranked_creators = popular_creators(posts)
    paginated, page, total_pages, total_items = get_paginated_list(
        ranked_creators)
    return render_template("creators.html", creators=paginated, page=page, total_pages=total_pages)


@app.route("/statistics")
def statistics():
    dataset_state = get_dataset_state()
    posts = dataset_state["posts"]
    stats = get_statistics(posts)
    return render_template("statistics.html", stats=stats)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("dataset")
    if file and file.filename:
        original_filename = secure_filename(file.filename)
        if not original_filename.lower().endswith(".txt"):
            return jsonify({"error": "Only .txt dataset files are supported."}), 400

        session_id = get_session_id()
        stored_filename = f"{session_id}_{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)

        try:
            file.save(filepath)
            loaded_posts = load_posts(filepath)
        except Exception as e:
            return jsonify({"error": f"Dataset parse failed: {str(e)}"}), 400
        finally:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

        dataset_state = get_dataset_state()
        dataset_state["posts"] = loaded_posts
        dataset_state["filename"] = original_filename
        clear_explore_cache(dataset_state)

        return jsonify({
            "message": "Dataset Loaded Successfully!",
            "filename": dataset_state["filename"],
            "count": len(dataset_state["posts"])
        })
    return jsonify({"error": "Upload Failed"}), 400


@app.route("/delete", methods=["POST"])
def delete_dataset():
    dataset_state = get_dataset_state()
    dataset_state["posts"] = []
    dataset_state["filename"] = None
    clear_explore_cache(dataset_state)
    return jsonify({"message": "Dataset cleared from memory and storage."})


if __name__ == "__main__":
    # Ensure it's broadcasted to your network for phone testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
