import subprocess
from generate import generate_article
from index_updater import update_index

# 🧠 Step 1: Define your article topics (can be automated with GNews/Trends)
keywords = [
    "Health benefits of turmeric",
    "Side effects of too much green tea",
    "Top AI tools for SEO in 2025",
    "Why Google favors fast-loading pages",
    "Best way to lose belly fat without gym"
]

# 📝 Step 2: Generate articles
for keyword in keywords:
    generate_article(keyword)

# 🏠 Step 3: Update homepage
update_index()

# 🚀 Step 4: Git add, commit, push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Auto-generated new articles and updated index"])
subprocess.run(["git", "push"])

print("\n✅ Blog updated and pushed to GitHub Pages!")