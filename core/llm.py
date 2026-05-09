from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(
    base_url=settings.OLLAMA_BASE_URL,
    api_key=settings.OLLAMA_API_KEY
)

def load_prompt():
    with open("prompts/system_prompt.txt", "r") as f:
        return f.read()

async def analyze_ideas_stream(messages: list):
    system_prompt = load_prompt()
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = await client.chat.completions.create(
        model=settings.OLLAMA_MODEL,
        messages=full_messages,
        temperature=0.6,
        stream=True 
    )

    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content