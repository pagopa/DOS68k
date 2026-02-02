from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional
from ..service import get_provider
from ..modules.settings import SETTINGS
from ..modules.logger import get_logger

LOGGER = get_logger(__name__)

router = APIRouter(prefix="/protected", tags=["JWT Protected"])

@router.get("/jwt-check", summary="Check JWT token")
def jwt_check(Authorization: Optional[str] = Header(None)):
    """
    Verify JWT token using the configured authentication provider.
    The provider is selected via the AUTH_PROVIDER environment variable.
    
    When AUTH_PROVIDER=local, the Authorization header is optional.
    """
    provider = get_provider()
    provider_type = SETTINGS.auth_provider.lower()
    LOGGER.info(f"JWT verification using provider: {provider_type}")
    
    # In modalità local, l'header Authorization è opzionale
    if provider_type == "local":
        LOGGER.debug("Local mode: Authorization header is optional")
        token = Authorization.split(" ", 1)[1] if Authorization and Authorization.startswith("Bearer ") else "mock-token"
        payload = provider.verify_jwt(token)
        LOGGER.info(f"Local mode: JWT verification successful for user {payload.get('sub')}")
        return {"status": "ok", "payload": payload}
    
    # Per altri provider, l'header è obbligatorio
    LOGGER.debug(f"Provider {provider_type}: Authorization header is required")
    if not Authorization:
        LOGGER.warning("JWT verification failed: Missing Authorization header")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Authorization header")
    if not Authorization.startswith("Bearer "):
        LOGGER.warning("JWT verification failed: Missing Bearer token prefix")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Bearer token")
    
    token = Authorization.split(" ", 1)[1]
    payload = provider.verify_jwt(token)
    LOGGER.info(f"JWT verification successful for user {payload.get('sub')}")
    return {"status": "ok", "payload": payload}


