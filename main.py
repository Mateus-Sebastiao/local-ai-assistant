from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import Base, engine
from core.middleware import setup_middleware
from routes import users, ai

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

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(ai.router, prefix="/api/analyze", tags=["AI Assistant"])