from fastapi import APIRouter, Depends

from ..db import get_db_session

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
        "service": "Chatbot API",
        "database": "connected",
    }
