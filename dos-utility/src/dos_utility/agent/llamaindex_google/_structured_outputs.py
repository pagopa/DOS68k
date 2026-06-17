from pydantic import BaseModel


class RAGOutput(BaseModel):
    """Structured output produced by an individual RAG tool call.

    Internal to the LlamaIndex + Google GenAI provider: it scopes what the
    RetrieverQueryEngine returns before the agent composes the final answer.
    """

    response: str
