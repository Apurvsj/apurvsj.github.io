import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ARTICLES_DIR = "articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")  # put this in .env

# 🔠 Slugify filename
def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

# 🔗 Get related article links
def get_related_articles(current_title, parent_title=None, top_n=3):
    current_words = set(current_title.lower().split())

    def clean_title_from_filename(filename):
        name = os.path.splitext(os.path.basename(filename))[0].replace("-", " ")
        return re.sub(r'\s+', ' ', name).strip()

    similarity_scores = []

    for file in os.listdir(ARTICLES_DIR):
        if not file.endswith(".html"):
            continue
        title = clean_title_from_filename(file)
        if title.lower() == current_title.lower():
            continue
        words = set(title.lower().split())
        score = len(current_words & words) / len(current_words | words)
        similarity_scores.append((score, file, title))

    related = sorted(similarity_scores, key=lambda x: -x[0])[:top_n]
    links = []

    if parent_title:
        parent_slug = slugify(parent_title)
        links.append(f'<li><a href="{parent_slug}.html">← Back to: {parent_title}</a></li>')

    links += [
        f'<li><a href="{file}">{title}</a></li>'
        for _, file, title in related
    ]
    return links

# ✍️ Generate one article
def generate_article(keyword, parent=None):
    title = keyword.strip().title()
    slug = slugify(title)
    filename = f"{slug}.html"
    filepath = os.path.join(ARTICLES_DIR, filename)

    if os.path.exists(filepath):
        print(f"⏯️ Skipping existing article: {filename}")
        return filename

    prompt = f"Write a detailed, SEO-optimized blog article on: '{keyword}'. Use headings, bullet points, and an engaging, news-style tone. Mention key facts, examples, and structure it well."

    messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8
    )

    content = response.choices[0].message.content

    # 🔗 Related links
    related_links = get_related_articles(title, parent_title=parent)
    related_html = ""
    if related_links:
        related_html = """
        <hr>
        <h3>📚 Related Articles</h3>
        <ul>
        {}
        </ul>
        """.format("\n".join(related_links))

    # 📄 Write article
    schema = f"""
    <script type=\"application/ld+json\">
    {{
      \"@context\": \"https://schema.org\",
      \"@type\": \"Article\",
      \"headline\": \"{title}\",
      \"datePublished\": \"{datetime.now().date()}\",
      \"author\": {{
        \"@type\": \"Person\",
        \"name\": \"Apurv Jha\"
      }},
      \"publisher\": {{
        \"@type\": \"Organization\",
        \"name\": \"AI SEO Blog\",
        \"logo\": {{
          \"@type\": \"ImageObject\",
          \"url\": \"https://apurvsj.github.io/seo-blog/logo.png\"
        }}
      }}
    }}
    </script>
    """

    article_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>{title}</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    {schema}
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

# 🔥 Fetch trending topics from GNews
def fetch_trending_keywords(n=10):
    url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&max={n}&token={GNEWS_API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        titles = [article["title"] for article in articles if article.get("title")]
        return list(set(titles))[:n]
    except Exception as e:
        print("\u26a0\ufe0f Failed to fetch trending topics:", e)
        return []

if __name__ == "__main__":
    trending = fetch_trending_keywords()
    for topic in trending:
        generate_article(topic)
