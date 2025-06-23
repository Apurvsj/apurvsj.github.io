import subprocess
from index_updater import update_index
from generate import fetch_trending_keywords, generate_article

# 🔥 Trending topics
trending = fetch_trending_keywords()

# ✍️ Generate articles
for topic in trending:
    generate_article(topic)

# 🏠 Update homepage
update_index()


# 🚀 Step 4: Git add, commit, push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Auto-generated new articles and updated index"])
subprocess.run(["git", "push"])

print("\n✅ Blog updated and pushed to GitHub Pages!")