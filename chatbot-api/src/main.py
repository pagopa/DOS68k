from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .env import settings
from .db import get_db_session
from .routers import health

app: FastAPI = FastAPI(
    title="Chatbot API",
    description="API for interacting with the Chatbot service.",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=health.router)

