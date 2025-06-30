from jinja2 import Environment, FileSystemLoader
from datetime import date

env = Environment(loader=FileSystemLoader("templates"))

def render_article_html(title, content, output_path):
    template = env.get_template("article_template.html")
    html = template.render(
        title=title,
        summary=content[:150],
        content=content.replace("\n", "<br>"),
        date=date.today().strftime("%B %d, %Y")
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
