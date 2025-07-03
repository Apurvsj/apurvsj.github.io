import os
import re
import requests
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai import RateLimitError
import random
from collections import defaultdict
from openai import APIError, Timeout


def safe_completion(client, **kwargs):
    max_retries = 6
    base_wait = 10
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError:
            wait_time = base_wait + random.randint(1, 5) + attempt * 5
            print(f"🔁 Rate limit hit. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except (APIError, Timeout) as e:
            print(f"⚠️ API error: {e}. Retrying...")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"❌ Other error: {e}")
            break
    raise Exception("❌ Failed after multiple retries.")


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ARTICLES_DIR = "articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)
print(f"🔍 Saving articles to: {os.path.abspath(ARTICLES_DIR)}")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

ADSENSE_SCRIPT = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8503468188860862"
     crossorigin="anonymous"></script>
"""

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def get_related_articles(current_title, parent_title=None, top_n=3):
    current_words = set(current_title.lower().split())

    def clean_title_from_filename(filename):
        name = filename.replace(".html", "").replace("-", " ")
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
        clean_parent = re.sub(r'(?i)^articles[/-]+', '', parent_title.strip())
        parent_slug = slugify(clean_parent)
        links.append(f'<li><a href="{parent_slug}.html">← Back to: {clean_parent.title()}</a></li>')
    links += [
        f'<li><a href="{filename}">{title.title()}</a></li>'
        for _, filename, title in related
    ]
    return links

def generate_article(keyword, parent=None):
    title = keyword.strip().title()
    slug = slugify(title)
    filename = f"{slug}.html"
    filepath = os.path.join(ARTICLES_DIR, filename)

    if os.path.exists(filepath):
        print(f"⏭️ Skipping existing article: {filename}")
        return filename

    prompt = f"""
Write a high-quality, SEO-optimized blog article about: "{keyword}"

Requirements:
- Start with a strong, engaging introduction
- Use proper HTML tags: <h2> for headings, <ul>/<li> for bullet points
- Add at least 1 FAQ section at the end with 2–3 common questions and answers
- Keep tone informative but natural (news-style, not robotic)
- Break long text into smaller paragraphs
- Include relevant facts or examples to increase authority
- Avoid repetition

Write the article in clean HTML format only (no markdown or plain text).
"""

    messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": prompt}
    ]

    response = safe_completion(
        client,
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=900
    )

    content = response.choices[0].message.content

    # Fix common SEO issues:
    content = re.sub(r'<title>.*?</title>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<h1>.*?</h1>', '', content, flags=re.IGNORECASE | re.DOTALL)

    text_only = re.sub(r'<[^>]+>', '', content)
    description = text_only.strip().split('\n')[0][:160] or title
    seo_title = title[:65] + ("…" if len(title) > 65 else "")

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

    url = f"https://apurvsj.github.io/articles/{filename}"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "author": {"@type": "Person", "name": "Apurv Jha"},
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "publisher": {"@type": "Organization", "name": "apurvsj.github.io"},
        "description": description,
        "mainEntityOfPage": url
    }
    schema_json = json.dumps(schema, indent=2)

    article_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>{seo_title}</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <meta name=\"description\" content=\"{description}\">
    <script type=\"application/ld+json\">
{schema_json}
    </script>
    {ADSENSE_SCRIPT}
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

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(article_html)
        print(f"✅ Article written: {filepath}")
    except Exception as e:
        print(f"❌ Failed to write article {filename}: {e}")
    return filename

def fetch_trending_keywords(n=5):
    url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&max={n}&token={GNEWS_API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        titles = [article["title"] for article in articles if article.get("title")]
        return list(set(titles))[:n]
    except Exception as e:
        print("⚠️ Failed to fetch trending topics:", e)
        return []

def update_sitemap():
    sitemap_path = "sitemap.xml"
    base_url = "https://apurvsj.github.io/"
    today = datetime.today().strftime("%Y-%m-%d")

    try:
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html")]
        urlset = ['<?xml version="1.0" encoding="UTF-8"?>']
        urlset.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for f in files:
            url_entry = f"""  <url>
    <loc>{base_url}{f}</loc>
    <lastmod>{today}</lastmod>
  </url>"""
            urlset.append(url_entry)

        urlset.append('</urlset>')

        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write("\n".join(urlset))

        print(f"✅ sitemap.xml updated with {len(files)} articles.")
    except Exception as e:
        print("❌ Failed to update sitemap.xml:", e)

def update_homepage_index():
    TOPIC_KEYWORDS = {
        "Science & Tech": ["nasa", "galaxy", "asteroid", "quantum", "camera", "exploration", "science"],
        "Gadgets & Launches": ["launch", "vivo", "iphone", "samsung", "xiaomi", "camera", "sale"],
        "Sports": ["cricket", "match", "pant", "tournament"],
        "Global Affairs": ["iran", "us", "israel", "global", "conflict", "strike"],
        "Health": ["health", "diet", "supplement", "fitness", "kidney", "heart", "attack"],
        "General News": ["train", "india", "update", "report", "news", "incident"]
    }

    grouped_articles = defaultdict(list)

    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html")]
    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(ARTICLES_DIR, f)), reverse=True)

    for filename in files:
        if filename.endswith(".html"):
            name = filename.replace(".html", "").replace("-", " ").lower()
            title = filename.replace(".html", "").replace("-", " ").title()
            url = f"{ARTICLES_DIR}/{filename}"
            matched = False
            for topic, keywords in TOPIC_KEYWORDS.items():
                if any(kw in name for kw in keywords):
                    grouped_articles[topic].append((title, url))
                    matched = True
                    break
            if not matched:
                grouped_articles["Other"].append((title, url))

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI SEO Blog by GPT</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f9f9f9; color: #222; padding: 1rem; }
    header { text-align: center; padding: 2rem 1rem; background-color: #4e54c8; color: white; border-radius: 1rem; }
    h1 { margin: 0; font-size: 2rem; }
    .section { margin: 2rem 0; }
    .card-container { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; }
    .card { background: white; padding: 1rem; border-radius: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 300px; }
    .card h2 { margin-top: 0; color: #4e54c8; }
    .card ul { list-style-type: none; padding-left: 0; }
    .card li { margin-bottom: 0.5rem; }
    .card a { text-decoration: none; color: #2c3e50; }
    .card a:hover { color: #4e54c8; }
    .all-articles-btn { display: inline-block; margin: 1.5rem auto; padding: 0.8rem 1.5rem; background: #4e54c8; color: white; text-decoration: none; font-weight: bold; border-radius: 8px; transition: background 0.3s ease; }
    .all-articles-btn:hover { background: #3a3ebf; }
    .more-link { display: block; text-align: right; font-size: 0.9rem; margin-top: 0.5rem; }
    footer { margin: 3rem 0; text-align: center; font-size: 0.9rem; color: #777; }
  </style>
</head>
<body>
  <header>
    <h1>📰 The Daily Pulse</h1>
    <p>Your front row seat to what's happening now</p>
    <a class="all-articles-btn" href="all.html">📚 View All Articles</a>
  </header>
  <div class="card-container">
'''
    for topic, articles in grouped_articles.items():
        short_list = articles[:2]
        html_content += f'<div class="card"><h2>{topic}</h2><ul>'
        for title, url in short_list:
            html_content += f'<li><a href="{url}">{title}</a></li>'
        html_content += '</ul>'
        html_content += f'<a class="more-link" href="{slugify(topic)}.html">More &rarr;</a>'
        html_content += '</div>'

    html_content += '''
  </div>
  <footer>
    Made with ❤️ using GPT · <a href="https://github.com/apurvsj/apurvsj.github.io">View Source</a>
  </footer>
</body>
</html>
'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html updated with card layout and latest articles.")

def update_all_articles_page():
    files = [
        f for f in os.listdir(ARTICLES_DIR)
        if f.endswith(".html")
    ]
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(ARTICLES_DIR, x)), reverse=True)

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>All Articles | apurvsj.github.io</title>
  <style>
    body { font-family: sans-serif; background: #f8f9fa; padding: 2rem; color: #333; }
    h1 { text-align: center; }
    ul { list-style-type: none; padding: 0; max-width: 800px; margin: 2rem auto; }
    li { background: #fff; margin: 10px 0; padding: 1rem; border-radius: 8px;
         box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: 0.2s ease; }
    li:hover { transform: scale(1.01); }
    a { text-decoration: none; color: #0077cc; font-weight: bold; }
    a:hover { color: #005fa3; }
  </style>
</head>
<body>
  <h1>🗂️ All Articles</h1>
  <ul>
'''

    for file in files:
        title = file.replace(".html", "").replace("-", " ").title()
        link = f"articles/{file}"
        html += f'    <li><a href="{link}">{title}</a></li>\n'

    html += '''  </ul>
  <p style="text-align: center; color: #777;">Updated on ''' + datetime.now().strftime("%B %d, %Y") + '''</p>
</body>
</html>'''

    with open("all.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ all.html created with links to all articles.")

def update_topic_pages(grouped_articles):
    for topic, articles in grouped_articles.items():
        slug = slugify(topic)
        filename = f"{slug}.html"

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{topic} Articles | apurvsj.github.io</title>
  <style>
    body {{ font-family: sans-serif; background: #f8f9fa; padding: 2rem; color: #333; }}
    h1 {{ text-align: center; }}
    ul {{ list-style-type: none; padding: 0; max-width: 800px; margin: 2rem auto; }}
    li {{ background: #fff; margin: 10px 0; padding: 1rem; border-radius: 8px;
         box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: 0.2s ease; }}
    li:hover {{ transform: scale(1.01); }}
    a {{ text-decoration: none; color: #0077cc; font-weight: bold; }}
    a:hover {{ color: #005fa3; }}
  </style>
</head>
<body>
  <h1>🗂️ {topic} Articles</h1>
  <ul>
'''

        for title, url in articles:
            html += f'    <li><a href="{url}">{title}</a></li>\n'

        html += f'''  </ul>
  <p style="text-align: center; color: #777;">Updated on {datetime.now().strftime("%B %d, %Y")}</p>
</body>
</html>'''

        with open(f"{filename}", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ {filename} generated.")

if __name__ == "__main__":
    trending = fetch_trending_keywords()
    for topic in trending:
        generate_article(topic)

    update_sitemap()
    update_homepage_index()
    update_all_articles_page()
    update_topic_pages(grouped_articles)