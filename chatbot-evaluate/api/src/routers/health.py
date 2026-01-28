from fastapi import APIRouter, Depends
from typing import Annotated
from dos_utility.database.sql import get_async_session
from dos_utility.queue import QueueInterface, get_queue_client


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
    dependencies=[Depends(dependency=get_async_session)],
)
async def health_check_db():
    # Health check endpoint to verify database connectivity
    return {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "database": "connected",
    }

@router.get(path="/queue", summary="Check Chatbot API queue connectivity")
async def health_check_queue(queue_client: Annotated[QueueInterface, Depends(dependency=get_queue_client)]):
    # Health check endpoint to verify queue connectivity
    healthy: bool = await queue_client.is_healthy()

    return {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "queue": "connected" if healthy is True else "NOT connected",
    }
