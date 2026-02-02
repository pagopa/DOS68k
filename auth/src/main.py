from fastapi import FastAPI

from .routers import health, jwt_check

app: FastAPI = FastAPI(
    title="Auth Service",
    description="Service for user authentication and authorization",
    docs_url="/",
)

app.include_router(router=health.router)
app.include_router(router=jwt_check.router)