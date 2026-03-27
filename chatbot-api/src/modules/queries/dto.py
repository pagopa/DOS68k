from typing import Annotated, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class Query(BaseModel):
    question: str
    answer: str

class CreateQueryDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(serialize_by_alias=True, validate_by_name=True)

    question: str
    knowledge_base: Annotated[Optional[str], Field(alias="knowledgeBase", default=None)]
    session_history: Annotated[Optional[List[Query]], Field(alias="sessionHistory", default=None)]

class QueryResponseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(serialize_by_alias=True, validate_by_name=True)

    id: UUID
    session_id: Annotated[UUID, Field(alias="sessionId")]
    question: str
    answer: str
    bad_answer: Annotated[bool, Field(alias="badAnswer")]
    topic: List[str]
    contexts: List[str]
    created_at: Annotated[str, Field(alias="createdAt")]
    expires_at: Annotated[Optional[str], Field(alias="expiresAt")]
