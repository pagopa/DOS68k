from fastapi import FastAPI

app: FastAPI = FastAPI(
    title="Auth Service",
    description="Service for user authentication and authorization",
    docs_url="/",
)

@app.get("/health")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {"status": "ok"}
