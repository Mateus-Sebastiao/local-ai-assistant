from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status, Request
from core.middleware import setup_middleware
import uuid
from core.llm import analyze_ideas
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models

from schemas import AnalyzeRequest

Base.metadata.create_all(engine)

app = FastAPI(title="Senior DevOps Assistant API")
setup_middleware(app) # Injecting our decoupled middleware

# @app.post("/api/analyze")
# async def analyze(user_prompt: str):
#     analysis = await analyze_ideas(user_prompt)
#     return {
#         "analysis": analysis,
#         "status": "success"
#     }

# @app.get("/health")
# async def health():
#     return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze(
    request: Request, # Inject request to access session
    data: AnalyzeRequest,
    db: Annotated[Session, Depends(get_db)]
):
    # 1. Get or Create Session ID from Middleware
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id

    # 2. Fetch history (Chronological Order)
    stmt = (
        select(models.ChatMessage)
        .where(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.id.asc())
    )
    db_messages = db.execute(stmt).scalars().all()

    # 3. Build AI Context
    history = [{"role": m.role, "content": m.content} for m in db_messages]
    history.append({"role": "user", "content": data.user_prompt})
    
    analysis = await analyze_ideas(history)

    # 4. Atomic Database Write
    try:
        new_messages = [
            models.ChatMessage(session_id=session_id, role="user", content=data.user_prompt),
            models.ChatMessage(session_id=session_id, role="assistant", content=analysis)
        ]
        db.add_all(new_messages)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Transaction Failed")

    return {"analysis": analysis}