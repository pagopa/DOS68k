from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from dos_utility.auth import UserRole


class JWTCheckResponseDTO(BaseModel):
    """Standard JWT claims (RFC 7519). Provider-specific extra claims are passed through."""
    model_config: ConfigDict = ConfigDict(extra="allow")

    sub: Annotated[str, Field(description="Subject — unique user identifier.")]
    iss: Annotated[str, Field(description="Issuer of the token.")]
    exp: Annotated[int, Field(description="Expiration time (Unix timestamp).")]
    iat: Annotated[int, Field(description="Issued-at time (Unix timestamp).")]
    email: Annotated[Optional[str], Field(default=None, description="User email address, if present in the token.")]
    role: Annotated[UserRole, Field(description="User role")]
