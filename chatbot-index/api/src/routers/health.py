from fastapi import APIRouter, Depends
from typing import Annotated
from redis.asyncio import Redis

from ..queue import get_queue_client

router: APIRouter = APIRouter(prefix="/health", tags=["Health checks"])

@router.get(path="", summary="Check Chatbot Index API service is running")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {
        "status": "ok",
        "service": "Chatbot Index API",
    }

@router.get(path="/queue", summary="Check Queue service is reachable")
async def health_check_queue(queue_client: Annotated[Redis, Depends(dependency=get_queue_client)]):
    # Health check endpoint to verify the queue service is reachable
    try:
        pong: bool = await queue_client.ping()

        return {
            "status": "ok",
            "service": "Chatbot Index API",
            "queue": "connected" if pong is True else "not connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Chatbot Index API",
            "queue": f"connection error: {str(e)}",
        }
