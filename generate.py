import os
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ARTICLES_DIR = "articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def get_related_articles(current_title, articles_dir=ARTICLES_DIR, top_n=3):
    current_words = set(current_title.lower().split())

    def clean_title_from_filename(filename):
        name = filename.replace(".html", "").replace("-", " ")
        return re.sub(r'\s+', ' ', name).strip()

    similarity_scores = []

    for file in os.listdir(articles_dir):
        if not file.endswith(".html"):
            continue
        title = clean_title_from_filename(file)
        if title.lower() == current_title.lower():
            continue
        words = set(title.lower().split())
        score = len(current_words & words) / len(current_words | words)
        similarity_scores.append((score, file, title))

    related = sorted(similarity_scores, key=lambda x: -x[0])[:top_n]
    return [
        f'<li><a href="{articles_dir}/{filename}">{title.title()}</a></li>'
        for _, filename, title in related
    ]

def generate_article(keyword):
    title = keyword.strip().title()
    slug = slugify(title)
    filename = f"{slug}.html"
    filepath = os.path.join(ARTICLES_DIR, filename)

    prompt = f"Write a detailed, SEO-optimized news-style blog article on: '{keyword}'. Use headings, bullet points, and a zingy, engaging tone. Include stats, quotes, or examples if needed. Structure the content well."

    messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8
    )

    content = response.choices[0].message.content

    related_links = get_related_articles(title)
    related_html = ""
    if related_links:
        related_html = """
        <hr>
        <h3>📚 Related Articles</h3>
        <ul>
        {}
        </ul>
        """.format("\n".join(related_links))

    article_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>{title}</h1>
    <p><em>Published on {datetime.now().strftime("%B %d, %Y")}</em></p>
    <hr>
    {content}
    {related_html}
</body>
</html>
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article_html)

    print(f"✅ Article saved to {filepath}")
    return filename
