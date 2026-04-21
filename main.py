from fastapi import FastAPI
from core.llm import analyze_ideas

app = FastAPI(title="Senior DevOps Assistant API")

@app.post("/api/analyze")
async def analyze(user_prompt: str):
    analysis = await analyze_ideas(user_prompt)
    return {
        "analysis": analysis,
        "status": "success"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
