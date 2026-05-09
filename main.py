from contextlib import asynccontextmanager
from typing import Annotated, List
import uuid

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Database & Models
from database import Base, engine, get_db
import models
import schemas

# Core Logic
from core.middleware import setup_middleware
from core.llm import analyze_ideas_stream
from core.security import get_password_hash

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan, title="Senior DevOps Assistant API")
setup_middleware(app) # Injecting our decoupled middleware

# --- USER MANAGEMENT (CRUD) ---

@app.post("/api/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Create a new user with hashed password validation.
    """
    # Check if user already exists (email or username)
    query = select(models.User).where(
        (models.User.email == user_in.email) | (models.User.username == user_in.username)
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email or username already exists"
        )

    # Hash password and save
    db_user = models.User(**user_in.model_dump(exclude={"password"}), 
                         hashed_password=get_password_hash(user_in.password))
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/api/users", response_model=List[schemas.UserResponse])
async def list_users(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Admin-like view to list all registered users.
    """
    users = await db.execute(select(models.User)).scalars().all()
    return users

@app.patch("/api/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int, 
    user_update: schemas.UserUpdate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Partial update of user details using PATCH.
    """
    db_user = await db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Filter only provided data (exclude_unset=True)
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Hard delete of a user record.
    """
    db_user = await db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    await db.commit()
    return None

# --- AI ASSISTANT ENDPOINTS ---

@app.post("/api/analyze/stream")
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