from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .env import get_settings
from .modules.health import health
from .modules.evaluate import controller as evaluate

app: FastAPI = FastAPI(
    title="Chatbot Evaluate API",
    description="API for interacting with the Chatbot Evaluate service.",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=health.router)
app.include_router(router=evaluate.router)