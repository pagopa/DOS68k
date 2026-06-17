from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dos_utility.tracing import get_tracer

from .env import get_settings
from .modules.sessions.controller import router as sessions_router
from .modules.queries.controller import router as query_router
from .modules.health.controller import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracer = get_tracer()
    async with tracer:
        yield
    await tracer.flush()


app: FastAPI = FastAPI(
    title="Chatbot API",
    description="API for interacting with the Chatbot service.",
    docs_url="/",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=health_router)
app.include_router(router=sessions_router)
app.include_router(router=query_router)
