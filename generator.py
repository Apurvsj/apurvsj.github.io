import os
from openai import OpenAI
from slugify import slugify

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_article(title):
    print(f"🔍 Generating article for: {title}")

    try:
        prompt = f"""Write a structured, zingy, and SEO-optimized news article for the headline:
"{title}"
Include:
- A clear title and subheading
- A compelling introduction
- Structured body content (can include lists or bullet points)
- A short conclusion
Avoid repetition. Make it human-readable and engaging."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional news journalist writing articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()
        content_html = content.replace('\n', '<br>')

        html_content = (
            "<html>\n"
            "<head>\n"
            f"<title>{title}</title>\n"
            '<meta charset="UTF-8">\n'
            "</head>\n"
            "<body style=\"font-family:Arial, sans-serif; line-height:1.6; max-width:800px; margin:auto;\">\n"
            f"<h1>{title}</h1>\n"
            "<hr>\n"
            f"<div>{content_html}</div>\n"
            "</body>\n"
            "</html>"
        )

        slug = slugify(title)
        os.makedirs("articles", exist_ok=True)
        output_path = f"articles/{slug}.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Article saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return None
