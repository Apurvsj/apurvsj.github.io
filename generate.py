import os
from datetime import date
from dotenv import load_dotenv
from renderer import render_article_html
from index_updater import update_index
from openai import OpenAI

load_dotenv()
client = OpenAI()  # This automatically reads from OPENAI_API_KEY in your .env

# Replace with your actual trending topics or dynamic fetch
trending_topics = [
    "India Stock Market Today",
    "AI Tools 2025",
    "How to Use ChatGPT in Education",
    "Latest Cricket Match Summary",
    "Top 10 Travel Destinations 2025",
]

os.makedirs("articles", exist_ok=True)

def generate_article(topic):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Write a detailed, SEO-optimized news article in a zingy tone."},
            {"role": "user", "content": f"Write a blog post on: {topic}"},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def slugify(text):
    return text.lower().replace(" ", "-").replace("?", "").replace(",", "")

def main():
    links = []
    for topic in trending_topics:
        content = generate_article(topic)
        slug = slugify(topic)
        filename = f"{slug}.html"
        filepath = os.path.join("articles", filename)
        render_article_html(topic, content, filepath)
        links.append((topic, f"articles/{filename}"))
    
    update_index(links)

if __name__ == "__main__":
    main()
