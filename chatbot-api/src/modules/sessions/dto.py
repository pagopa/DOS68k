from uuid import UUID
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field

class CreateSessionDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(validate_by_alias=True)

    title: str
    is_temporary: Annotated[bool, Field(alias="isTemporary", default=False)]

class SessionResponseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(serialize_by_alias=True, validate_by_name=True)

    id: UUID
    user_id: Annotated[UUID, Field(alias="userId")]
    title: str
    created_at: Annotated[str, Field(alias="createdAt")]
    expires_at: Annotated[Optional[str], Field(alias="expiresAt")]