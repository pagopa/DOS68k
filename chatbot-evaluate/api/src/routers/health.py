from fastapi import APIRouter, Depends
from typing import Annotated
from redis.asyncio import Redis

from ..db import get_db_session
from ..queue import get_queue_client

router: APIRouter = APIRouter(prefix="/health", tags=["Health checks"])

@router.get(path="", summary="Check Chatbot Evaluate API service is running")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {
        "status": "ok",
        "service": "Chatbot Evaluate API",
    }

@router.get(
    path="/db",
    summary="Check Chatbot API database connectivity",
    dependencies=[Depends(dependency=get_db_session)],
)
async def health_check_db():
    # Health check endpoint to verify database connectivity
    return {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "database": "connected",
    }

@router.get(path="/queue", summary="Check Chatbot API queue connectivity")
async def health_check_queue(queue_client: Annotated[Redis, Depends(dependency=get_queue_client)]):
    # Health check endpoint to verify queue connectivity
    try:
        pong: bool = await queue_client.ping()

        return {
            "status": "ok",
            "service": "Chatbot Evaluate API",
            "queue": "connected" if pong is True else "not connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Chatbot Evaluate API",
            "queue": f"connection error: {str(e)}",
        }
