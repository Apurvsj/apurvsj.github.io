from generate import fetch_trending_keywords, generate_article
from index_updater import update_index
from openai import OpenAI
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌳 Get 5–10 trending topics
root_topics = fetch_trending_keywords(n=5)

# 🤖 Ask GPT to generate subtopics for a given topic
def generate_subtopics(root_topic):
    prompt = f"Generate 3 closely related SEO blog subtopics (as a list) for the article title: '{root_topic}'. Return only the list."
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    text = response.choices[0].message.content.strip()
    # 🧼 Clean list
    subtopics = [line.strip("-•1234567890. ").strip() for line in text.splitlines() if line.strip()]
    return subtopics[:1]

# 🧠 Generate article clusters
for root in root_topics:
    print(f"\n📌 Main: {root}")
    generate_article(root)
    subtopics = generate_subtopics(root)
    for sub in subtopics:
        print(f"  └─📄 Sub: {sub}")
        generate_article(sub, parent=root)

# 🏠 Update homepage
update_index()

# 🚀 Push to GitHub
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Auto-generated SEO topic clusters"])
subprocess.run(["git", "push"])

print("\n✅ All clusters published!")
