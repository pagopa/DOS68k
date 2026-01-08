from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/health")
async def health_check():
    # Simple health check endpoint to verify the service is running
    return {"status": "ok"}
