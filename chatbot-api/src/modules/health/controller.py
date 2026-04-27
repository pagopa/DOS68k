from typing import Annotated
from fastapi import APIRouter, Depends

from dos_utility.database.nosql import get_nosql_client, NoSQLInterface


router: APIRouter = APIRouter(prefix="/health", tags=["Health Checks"])


@router.get(path="", summary="Check Chatbot API service is running")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {
        "status": "ok",
        "service": "Chatbot API",
    }


@router.get(
    path="/db",
    summary="Check Chatbot API database connectivity",
)
async def health_check_db(
    db: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)],
):
    # Health check endpoint to verify database connectivity
    is_healthy: bool = await db.is_healthy()

    return {
        "status": "ok",
        "service": "Chatbot API",
        "database": "connected" if is_healthy is True else "NOT connected",
    }
