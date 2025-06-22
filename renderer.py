from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

def render_article(article_data, output_file):
    template = env.get_template("article_template.html")

    html = template.render(
        title=article_data["title"],
        body=article_data["body"],
        image=article_data["image"]
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)