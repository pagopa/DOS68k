from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SimpleFeedbackResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    query_id: Annotated[str, Field(alias="queryId")]
    session_id: Annotated[UUID, Field(alias="sessionId")]
    created_at: Annotated[str, Field(alias="createdAt")]