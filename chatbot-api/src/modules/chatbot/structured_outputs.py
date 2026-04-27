from typing import List, Annotated
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """A source document retrieved from the vector database."""

    source: str


class RAGOutput(BaseModel):
    """Structured output for individual RAG tool calls."""

    response: str


class DOS68KAgentOutput(BaseModel):
    """Final structured output produced by the agent."""

    response: Annotated[
        str,
        Field(
            description="The generated answer to the user's query in Markdown format."
        ),
    ]
    # tags: Annotated[List[str], Field(default=[], description="Topic tags extracted from the response, useful for categorization and filtering of conversation history.")]
