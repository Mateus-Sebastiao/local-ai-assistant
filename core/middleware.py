from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings

def setup_middleware(app: FastAPI):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="ai_assistant_sid",
        # Only enforce HTTPS if we are in production
        https_only=True if settings.ENV == "production" else False,
        same_site="lax"
    )
