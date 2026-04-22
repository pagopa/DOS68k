from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SimpleFeedbackResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True, extra="allow"
    )

    id: str
    session_id: Annotated[str, Field(alias="sessionId")]
    feedback: Annotated[bool, Field(alias="feedback")]


class EvaluationResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    query_id: Annotated[str, Field(alias="queryId")]
    question: Optional[str] = None
    answer: Optional[str] = None
    feedback: int


class EvaluationAllResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    evaluations: List[EvaluationResponse]