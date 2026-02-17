from fastapi import FastAPI

from .modules.mask import mask_router
from .modules.health import health_router

app: FastAPI = FastAPI(
    title="Masking Service",
    description="Service for masking PII in user/assistant queries",
    docs_url="/",
)

app.include_router(router=health_router)
app.include_router(router=mask_router)