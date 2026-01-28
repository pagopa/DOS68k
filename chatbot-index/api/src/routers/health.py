from fastapi import APIRouter, Depends
from typing import Annotated

from dos_utility.storage.aws import AWSS3
from dos_utility.queue import QueueInterface, get_queue_client


router: APIRouter = APIRouter(prefix="/health", tags=["Health checks"])

@router.get(path="", summary="Check Chatbot Index API service is running")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {
        "status": "ok",
        "service": "Chatbot Index API",
    }

@router.get(path="/queue", summary="Check Queue service is reachable")
async def health_check_queue(queue_client: Annotated[QueueInterface, Depends(dependency=get_queue_client)]):
    # Health check endpoint to verify the queue service is reachable
    is_healthy: bool = await queue_client.is_healthy()

    return {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "connected" if is_healthy is True else "NOT connected",
    }

@router.get(path="/storage", summary="Check Storage service is reachable")
async def health_check_storage():
    # Placeholder for storage health check logic

    try:
        s3: AWSS3 = AWSS3()
        s3.health_check()

        return {
            "status": "ok",
            "service": "Chatbot Index API",
            "storage": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Chatbot Index API",
            "storage": f"connection error: {str(e)}",
        }
