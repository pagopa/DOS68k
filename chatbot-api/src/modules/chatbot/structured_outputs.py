from typing import Annotated
from pydantic import BaseModel, Field


class DOS68KAgentOutput(BaseModel):
    """Final structured output produced by the agent."""

    response: Annotated[
        str,
        Field(
            description="The generated answer to the user's query in Markdown format."
        ),
    ]
    # tags: Annotated[List[str], Field(default=[], description="Topic tags extracted from the response, useful for categorization and filtering of conversation history.")]
