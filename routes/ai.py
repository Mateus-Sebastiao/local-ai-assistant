import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import models
import schemas
from core.llm import analyze_ideas_stream

router = APIRouter()

@router.post("/stream")
async def analyze(
    request: Request, # Inject request to access session
    data: schemas.AnalyzeRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
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
    result = await db.execute(stmt)
    db_messages = result.scalars().all()

    # 3. Build AI Context
    history = [{"role": m.role, "content": m.content} for m in db_messages]
    history.append({"role": "user", "content": data.user_prompt})

    # 4. Atomic Database Write
    async def stream_and_save():
        full_response = ""
        
        async for chunk in analyze_ideas_stream(history):
            full_response += chunk
            yield chunk
        
        try:
            new_messages = [
                models.ChatMessage(session_id=session_id, role="user", content=data.user_prompt),
                models.ChatMessage(session_id=session_id, role="assistant", content=full_response)
            ]
            db.add_all(new_messages)
            await db.commit()
            print("Historic saved!")
        except Exception as e:
            await db.rollback()
            print(f"Error to save: {e}")

    return StreamingResponse(stream_and_save(), media_type="text/plain")