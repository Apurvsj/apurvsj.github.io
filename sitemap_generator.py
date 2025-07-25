import os
from datetime import datetime

ARTICLES_DIR = "articles"
BASE_URL = "https://apurvsj.github.io/"

def generate_sitemap():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for articles directory: {ARTICLES_DIR}")
    
    # Check if articles directory exists
    if not os.path.exists(ARTICLES_DIR):
        print(f"❌ Error: {ARTICLES_DIR} directory not found!")
        print("Available directories:")
        for item in os.listdir("."):
            if os.path.isdir(item):
                print(f"  - {item}")
        return
    
    print(f"✅ Found {ARTICLES_DIR} directory")
    
    urls = []
    files_found = []
    
    for file in os.listdir(ARTICLES_DIR):
        files_found.append(file)
        if file.endswith(".html"):
            url = f"{BASE_URL}/{ARTICLES_DIR}/{file}"
            urls.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.today().date()}</lastmod>
  </url>""")
    
    print(f"Files found in {ARTICLES_DIR}: {files_found}")
    print(f"HTML files found: {len([f for f in files_found if f.endswith('.html')])}")
    
    if not urls:
        print("❌ No HTML files found to add to sitemap!")
        return
    
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    
    try:
        with open("sitemap.txt", "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        print("✅ sitemap.txt generated successfully.")
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    generate_sitemap()