from openai import OpenAI
from pytrends.request import TrendReq
from secretsy import openai_api_key
from jinja2 import Environment, FileSystemLoader
import os

client = OpenAI(api_key=openai_api_key)

def fetch_trending_keywords():
    pytrends = TrendReq()
    attempts = [
        ("real-time trending", "india"),
        ("real-time trending", "united_states"),
        ("daily trending", "india"),
        ("daily trending", "united_states"),
    ]

    for label, region in attempts:
        try:
            print(f"🌐 Trying {label}: {region.title()}")
            if label == "real-time trending":
                keywords_df = pytrends.realtime_trending_searches(pn=region)
            else:
                keywords_df = pytrends.trending_searches(pn=region)
            return keywords_df.iloc[:, 0].head(5).tolist()
        except Exception as e:
            print(f"⚠️ Failed: {region.title()} {label}. Trying next...")

    print("❌ All attempts failed: Google Trends unavailable.")
    print("⚡ Using fallback keywords.")
    return ["AI in Education", "Sustainable Travel", "ChatGPT Plugins", "Electric Vehicles 2025", "Space Tourism India"]

def generate_article(keyword):
    prompt = f"""Write a 600-word SEO-optimized blog post on '{keyword}'.
Include a catchy title, introduction, three subheadings, conclusion, and a 160-character meta description."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

def render_to_html(title, body, filename):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('blog_template.html')
    output = template.render(title=title, body=body)

    os.makedirs("articles", exist_ok=True)
    with open(f"articles/{filename}.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    keywords = fetch_trending_keywords()
    for keyword in keywords:
        content = generate_article(keyword)
        filename = keyword.lower().replace(" ", "-").replace("'", "")[:50]
        render_to_html(keyword, content, filename)
        print(f"✅ Article generated: {filename}.html")