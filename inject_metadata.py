import os
from bs4 import BeautifulSoup
from datetime import datetime

ARTICLES_DIR = "articles"
AUTHOR_NAME = "Apurv Jha"
BASE_URL = "https://apurvsj.github.io/articles/"

def clean_text(text):
    return text.replace("-", " ").replace(".html", "").title()

def generate_schema(title, description, url):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "author": {
            "@type": "Person",
            "name": AUTHOR_NAME
        },
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "publisher": {
            "@type": "Organization",
            "name": "apurvsj.github.io"
        },
        "description": description,
        "mainEntityOfPage": url
    }

for filename in os.listdir(ARTICLES_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(ARTICLES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Derive title from <h1> or filename
        h1 = soup.find("h1")
        title_text = h1.get_text() if h1 else clean_text(filename)
        description_text = soup.p.get_text() if soup.p else f"Read more about {title_text}"
        article_url = BASE_URL + filename

        # Inject <title> and <meta>
        if soup.head:
            soup.head.title.decompose() if soup.head.title else None
            soup.head.insert(0, soup.new_tag("title"))
            soup.head.title.string = title_text

            meta_tag = soup.new_tag("meta", attrs={"name": "description", "content": description_text})
            soup.head.append(meta_tag)

            # Add JSON-LD schema
            import json
            schema_data = generate_schema(title_text, description_text, article_url)
            script_tag = soup.new_tag("script", type="application/ld+json")
            script_tag.string = json.dumps(schema_data, indent=2)
            soup.head.append(script_tag)

        # Write back updated file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        print(f"✅ Updated: {filename}")
