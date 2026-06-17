from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, PositiveInt


class ChatTurn(BaseModel):
    """A single turn of conversation history fed to the agent."""

    question: Annotated[str, Field(description="The user's question for this turn.")]
    answer: Annotated[
        Optional[str],
        Field(
            default=None,
            description="The assistant's answer. None if this turn has not yet been answered.",
        ),
    ]


class ContextChunk(BaseModel):
    """A retrieved document chunk attached to an agent response."""

    filename: Annotated[
        str, Field(description="Name of the source file the chunk comes from.")
    ]
    chunk_id: Annotated[
        int, Field(description="Chunk identifier within the source file.")
    ]
    content: Annotated[str, Field(description="Raw text content of the chunk.")]
    score: Annotated[
        Optional[float],
        Field(
            default=None,
            description="Similarity score in [0, 1] when available, None otherwise.",
        ),
    ]


class AgentResponse(BaseModel):
    """Structured response produced by `AgentInterface.chat_generate`."""

    response: Annotated[
        str, Field(description="The final natural-language answer for the user.")
    ]
    tags: Annotated[
        List[str],
        Field(
            default_factory=list,
            description="Topic tags extracted from the response, if any.",
        ),
    ]
    context: Annotated[
        List[ContextChunk],
        Field(
            default_factory=list,
            description="Document chunks retrieved by RAG tool calls, sorted by descending score.",
        ),
    ]


class RagToolSpec(BaseModel):
    """Specification of a single RAG tool backed by a vector index.

    The provider implementation is responsible for materialising this
    spec into a concrete tool (e.g. wiring a retriever, building prompt
    templates, etc.).
    """

    index_id: Annotated[
        str, Field(description="Name of the index in the vector database.")
    ]
    name: Annotated[
        str,
        Field(description="Unique tool name exposed to the agent (no whitespace)."),
    ]
    description: Annotated[
        str,
        Field(
            description="Natural-language description used by the agent to decide when to call the tool."
        ),
    ]
    similarity_top_k: Annotated[
        Optional[PositiveInt],
        Field(
            default=None,
            description="Override the provider default for similarity_top_k.",
        ),
    ]
    qa_prompt: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Custom QA prompt template. Must expose {context_str} and {query_str} variables.",
        ),
    ]
    refine_prompt: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Custom refine prompt template. Must expose {existing_answer} and {context_msg} variables.",
        ),
    ]


class AgentConfig(BaseModel):
    """High-level configuration shared across providers."""

    name: Annotated[Optional[str], Field(default=None, description="Agent name.")]
    description: Annotated[
        Optional[str],
        Field(default=None, description="Natural-language description of the agent."),
    ]
    system_prompt: Annotated[
        Optional[str],
        Field(
            default=None,
            description="System prompt prepended to every conversation.",
        ),
    ]
    system_header: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Provider-specific reasoning header template (e.g. the ReAct system header).",
        ),
    ]
