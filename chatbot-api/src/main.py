from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .env import settings

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


@app.get("/health")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {"status": "ok"}
