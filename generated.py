from generator import generate_article
from fetch_trends import fetch_trending_keywords

print("🌐 Fetching headlines from GNews API")
keywords = fetch_trending_keywords()

if not keywords:
    print("⚠️ No trending keywords found.")
else:
    for keyword in keywords[:15]:
        generate_article(keyword)
