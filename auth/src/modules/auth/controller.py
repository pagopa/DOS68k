from typing import Optional, Annotated, Dict, Any
from fastapi import APIRouter, Header, Depends, status

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
        auth_service: Annotated[AuthService, Depends(dependency=get_auth_service)],
        authorization: Annotated[Optional[str], Header()], # Automatically reads the "Authorization" header (it takes the name from the function parameter name - case INsensitive)
    ) -> Dict[str, Any]:
    return auth_service.jwt_check(authorization=authorization)
