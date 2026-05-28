from typing import Annotated, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class Query(BaseModel):
    question: str
    answer: str


class CreateQueryDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    question: str
    session_history: Annotated[
        Optional[List[Query]], Field(alias="sessionHistory", default=None)
    ]


class Source(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    chunk_id: Annotated[int, Field(alias="chunkId")]
    content: str
    score: Optional[float]
    filename: str


class Scores(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )
    relevancy: float
    faithfulness: float
    utilization: float


class QueryResponseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    id: UUID
    session_id: Annotated[UUID, Field(alias="sessionId")]
    question: str
    answer: str
    topic: List[str]
    context: List[Source]
    created_at: Annotated[str, Field(alias="createdAt")]
    expires_at: Annotated[Optional[str], Field(alias="expiresAt")]
    tracing_trace_id: Annotated[
        Optional[str], Field(alias="tracingTraceId", default=None)
    ]
    is_evaluated: Annotated[bool, Field(default=False, alias="isEvaluated")]
    scores: Annotated[
        Optional[Scores], Field(default=None)
    ]
