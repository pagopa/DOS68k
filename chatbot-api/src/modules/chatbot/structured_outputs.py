from typing import Annotated, List
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """A source document the answer is based on."""

    title: Annotated[str, Field(description="Title of the source document.")]
    url: Annotated[str, Field(description="URL of the source document.")]


class RAGOutput(BaseModel):
    """Structured output for individual RAG tool calls."""

    response: str
    references: Annotated[
        List[Reference],
        Field(
            default=[],
            description="The source documents of the retrieved context used to answer, taken from their title and url.",
        ),
    ]


class DOS68KAgentOutput(BaseModel):
    """Final structured output produced by the agent."""

    response: Annotated[
        str,
        Field(
            description="The generated answer to the user's query in Markdown format."
        ),
    ]
    references: Annotated[
        List[Reference],
        Field(
            default=[],
            description="The source documents the answer is based on. Only cite documents taken from the retrieved context.",
        ),
    ]
    # tags: Annotated[List[str], Field(default=[], description="Topic tags extracted from the response, useful for categorization and filtering of conversation history.")]
