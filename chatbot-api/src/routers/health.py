from fastapi import APIRouter, Depends

from dos_utility.database.sql import get_async_session


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
    dependencies=[Depends(dependency=get_async_session)],
)
async def health_check_db():
    # Health check endpoint to verify database connectivity
    return {
        "status": "ok",
        "service": "Chatbot API",
        "database": "connected",
    }
