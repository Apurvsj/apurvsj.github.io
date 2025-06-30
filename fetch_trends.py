import requests
import os

def fetch_trending_keywords():
    print("🌐 Fetching headlines from GNews API")

    API_KEY = "83f29522f6b94f6701c1b8242a53d817"  # Replace this with your actual API key
    GNEWS_URL = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&max=10&token={API_KEY}"

    try:
        response = requests.get(GNEWS_URL)
        response.raise_for_status()
        data = response.json()
        headlines = [article['title'] for article in data.get('articles', []) if article.get('title')]

        if headlines:
            print(f"✅ Fetched keywords: {headlines[:5]}")
            return headlines[:5]
        else:
            print("⚠️ No keywords found in response.")
            return []

    except Exception as e:
        print(f"❌ Error fetching headlines: {e}")
        return []
