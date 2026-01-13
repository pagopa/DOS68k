from fastapi import APIRouter


router: APIRouter = APIRouter(prefix="/health", tags=["Health checks"])

@router.get(path="")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {
        "status": "ok",
        "service": "Auth Service",
    }