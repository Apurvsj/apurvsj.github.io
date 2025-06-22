def update_index(article_links):
    lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='UTF-8'><title>SEO Articles</title></head><body>",
        "<h1>Latest SEO Articles</h1><ul>"
    ]
    for title, href in article_links:
        lines.append(f'<li><a href="{href}">{title}</a></li>')
    lines.append("</ul></body></html>")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
