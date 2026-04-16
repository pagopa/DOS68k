from fastapi import FastAPI

from .modules.health.controller import router as health_router
from .modules.auth.controller import router as auth_router

app: FastAPI = FastAPI(
    title="Auth Service",
    description="Service for user authentication and authorization",
    docs_url="/",
)

app.include_router(router=health_router)
app.include_router(router=auth_router)