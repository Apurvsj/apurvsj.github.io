import os

def update_index(articles_dir="articles", output_file="index.html"):
    articles = sorted(os.listdir(articles_dir), reverse=True)
    links = ""
    for article in articles:
        if article.endswith(".html"):
            links += f'<li><a href="{articles_dir}/{article}">{article.replace(".html", "").replace("-", " ").title()}</a></li>\n'

    index_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>AI SEO Blog</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>📰 The Daily Pulse</h1>
    <p>Your front row seat to what's happening now</p>
    <ul>
        {links}
    </ul>
    <p>Made with ❤️ using GPT · <a href="https://github.com/apurvsj/seo-blog">View on GitHub</a></p>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_content)

if __name__ == "__main__":
    update_index()
