from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def list_articles():
    articles_dir = "articles"
    files = [f for f in os.listdir(articles_dir) if f.endswith(".html")]
    links = [f'<li><a href="/articles/{f}">{f}</a></li>' for f in files]
    return f"<h1>SEO Articles</h1><ul>{''.join(links)}</ul>"

@app.route("/articles/<path:filename>")
def serve_article(filename):
    return send_from_directory("articles", filename)

if __name__ == "__main__":
    app.run(debug=True)
