import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🔐 Using API Key:", os.getenv("OPENAI_API_KEY")[:10])

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hi in one sentence."}
    ],
    max_tokens=20,
    temperature=0.5
)

print(response.choices[0].message.content)
