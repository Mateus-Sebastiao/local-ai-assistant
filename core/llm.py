from openai import OpenAI
from core.config import settings

client = OpenAI(
    base_url=settings.OLLAMA_BASE_URL,
    api_key=settings.OLLAMA_API_KEY
)

def load_prompt():
    with open("prompts/system_prompt.txt", "r") as f:
        return f.read()

async def analyze_ideas(user_prompt: str):
    system_prompt = load_prompt()

    response = client.chat.completions.create(
        model=settings.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content
