from uuid import UUID
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field

class CreateSessionDTO(BaseModel):
    title: str

class SessionResponseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(serialize_by_alias=True)

    id: UUID
    title: str
    created_at: Annotated[str, Field(alias="createdAt")]
    # expires_at: Annotated[str, Field(alias="expiresAt")]
    expires_at: Annotated[Any, Field(alias="expiresAt")]