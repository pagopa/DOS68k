from typing import List
from pydantic import BaseModel, Field


# Product names used in tool descriptions and response metadata
PRODUCTS = "pagoPA, IO, SEND"


class Reference(BaseModel):
    title: str
    url: str


class RAGOutput(BaseModel):
    """Structured output for individual RAG tool calls."""
    response: str
    references: List[Reference] = Field(default_factory=list)


class FollowUpQuestionsOutput(BaseModel):
    """Structured output for the follow-up questions (chips) tool."""
    questions: List[str] = Field(default_factory=list)


class DiscoveryOutput(BaseModel):
    """Final structured output produced by the discovery agent."""
    response: str
    products: List[str] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
