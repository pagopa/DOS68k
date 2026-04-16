from typing import Annotated, List, Optional, Dict
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


class FileContext(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    chunk_id: Annotated[int, Field(alias="chunkId")]
    content: str
    score: Optional[float]


class QueryResponseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    id: UUID
    session_id: Annotated[UUID, Field(alias="sessionId")]
    question: str
    answer: str
    bad_answer: Annotated[bool, Field(alias="badAnswer")]
    topic: List[str]
    context: Dict[str, List[FileContext]]
    created_at: Annotated[str, Field(alias="createdAt")]
    expires_at: Annotated[Optional[str], Field(alias="expiresAt")]
