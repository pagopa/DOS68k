from typing import Optional, Annotated, Dict, Any
from fastapi import APIRouter, Header, Depends, Response, status

from .service import AuthService, get_auth_service
from .dto import JWTCheckResponseDTO

router: APIRouter = APIRouter(prefix="/protected", tags=["JWT Protected"])


@router.get(
    path="/jwt-check",
    response_model=JWTCheckResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Check JWT token",
)
def jwt_check(
    response: Response,
    auth_service: Annotated[AuthService, Depends(dependency=get_auth_service)],
    authorization: Annotated[Optional[str], Header()] = None,
) -> Dict[str, Any]:
    # Forward-auth contract: gateways (e.g. Traefik) read X-User-Id / X-User-Role
    # from the response headers and propagate them to the downstream request.
    claims = auth_service.jwt_check(authorization=authorization)
    response.headers["X-User-Id"] = str(claims["sub"])
    response.headers["X-User-Role"] = str(claims["role"])

    return claims
