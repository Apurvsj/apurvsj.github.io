import os
from datetime import datetime

ARTICLES_DIR = "articles"
BASE_URL = "https://apurvsj.github.io/"

def generate_sitemap():
    # Create both versions
    urls = []
    for file in os.listdir(ARTICLES_DIR):
        if file.endswith(".html"):
            url = f"{BASE_URL}/{ARTICLES_DIR}/{file}"
            urls.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.today().date()}</lastmod>
  </url>""")
    
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    
    # Keep the working .txt version
    with open("sitemap.txt", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    # Also create in assets folder to avoid root-level conflicts
    os.makedirs("assets", exist_ok=True)
    with open("assets/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print("✅ Both sitemap.txt and assets/sitemap.xml generated successfully.")

if __name__ == "__main__":
    generate_sitemap()