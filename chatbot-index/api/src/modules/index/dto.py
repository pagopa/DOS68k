from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class CreateIndexResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    index_id: Annotated[str, Field(alias="indexId")]
    user_id: Annotated[UUID, Field(alias="userId")]
    created_at: Annotated[str, Field(alias="createdAt")]
