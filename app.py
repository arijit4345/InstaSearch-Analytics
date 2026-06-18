from flask import Flask, render_template
from data_loader import load_posts

app = Flask(__name__)

posts = load_posts("dataset.txt")

@app.route("/")
def home():
    print(f"Loaded {len(posts)} posts")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)