from typing import Self, Dict, List, Any, Optional, Annotated
from pydantic import Field
from pathlib import Path
from workflows import Context
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ReActAgent, AgentOutput
from llama_index.core.llms import ChatMessage

from src.modules.chatbot.env import ChatbotSettings
from src.modules.chatbot.agent.settings import AgentYamlSettings


class GoogleGenAIMock(GoogleGenAI):
    def __new__(cls, **kwargs):
        instance = object.__new__(cls)
        object.__setattr__(instance, "__pydantic_fields_set__", set())
        object.__setattr__(instance, "__pydantic_extra__", None)
        object.__setattr__(instance, "__pydantic_private__", {"_max_tokens": 1000})
        object.__setattr__(instance, "context_window", 4096)
        object.__setattr__(instance, "model", "gemini-2.5-flash")
        object.__setattr__(instance, "is_function_calling_model", True)
        return instance

    def __init__(self: Self, **kwargs):
        pass


class GoogleGenAIEmbeddingMock(GoogleGenAIEmbedding):
    # Same pattern as ReActAgentMock: GoogleGenAIEmbedding is a Pydantic BaseModel,
    # so we use object.__new__ to allocate the instance and seed the two Pydantic v2
    # internals that __getattr__/__setattr__ depend on, bypassing real initialization.
    def __new__(cls, **kwargs):
        instance = object.__new__(cls)
        object.__setattr__(instance, "__pydantic_fields_set__", set())
        object.__setattr__(instance, "__pydantic_extra__", None)
        return instance

    def __init__(self: Self, **kwargs):
        pass


def get_chatbot_settings_mock() -> ChatbotSettings:
    class ChatbotSettingsMock(ChatbotSettings):
        provider: Annotated[str, Field(default="google")]
        model_id: Annotated[str, Field(default="model-id")]
        model_api_key: Annotated[str, Field(default="model-api-key")]
        embed_model_id: Annotated[str, Field(default="embed-model-id")]

    return ChatbotSettingsMock()


def get_llm_mock(**kwargs) -> LLM:
    return GoogleGenAIMock()


def get_embed_model_mock(**kwargs) -> BaseEmbedding:
    return GoogleGenAIEmbeddingMock()


def load_tools_mock(**kwargs) -> Dict[str, QueryEngineTool]:
    class QueryEngineToolMock(QueryEngineTool):
        def __init__(self: Self):
            pass

    return {
        "tool1": QueryEngineToolMock(),
        "tool2": QueryEngineToolMock(),
        "tool3": QueryEngineToolMock(),
    }


def get_agent_yaml_settings_mock(file: Path) -> AgentYamlSettings:
    return AgentYamlSettings(name="TestAgent", description="Test agent description")


DEFAULT_NODE_METADATA: List[Dict[str, Any]] = [
    {
        "filename": "file1.pdf",
        "chunk_id": "1",
        "url": "https://example.com/file1",
        "title": "File 1",
    }
]


def make_agent_mock(
    structured_response: Any = None,
    nodes_metadata: Optional[List[Dict[str, Any]]] = None,
):
    """Build a get_agent replacement whose run() returns the given structured
    response and retrieved nodes."""
    if structured_response is None:
        structured_response = {"response": "Test answer"}
    if nodes_metadata is None:
        nodes_metadata = DEFAULT_NODE_METADATA

    class NodeMock:
        def __init__(self: Self, metadata: Dict[str, Any]):
            self.metadata = metadata
            self.text = "some content"
            self.score = 0.9

    class RawOutputMock:
        source_nodes = [NodeMock(metadata) for metadata in nodes_metadata]

    class ToolOutputMock:
        raw_output = RawOutputMock()

    class ToolCallMock:
        tool_output = ToolOutputMock()

    class AgentOutputMock:
        pass

    AgentOutputMock.structured_response = structured_response
    AgentOutputMock.tool_calls = [ToolCallMock()]

    class ReActAgentMock(ReActAgent):
        def __init__(self: Self):
            pass

        async def run(self: Self, **kwargs) -> AgentOutput:
            # Return a plain duck-typed object: chat_generate only reads
            # .structured_response and .tool_calls, so AgentOutput is not needed.
            return AgentOutputMock()

    def get_agent(**kwargs) -> ReActAgent:
        return ReActAgentMock()

    return get_agent


get_agent_mock = make_agent_mock()


def get_agent_run_exception_mock(**kwargs) -> ReActAgent:
    class ReActAgentMock(ReActAgent):
        def __init__(self: Self):
            pass

        async def run(self: Self, **kwargs):
            raise Exception

    return ReActAgentMock()


def get_agent_invalid_structured_response_mock(**kwargs) -> ReActAgent:
    class ReActAgentMock(ReActAgent):
        def __init__(self: Self):
            pass

        async def run(self: Self, **kwargs) -> AgentOutput:
            # structured_response=None is the only non-dict value accepted by
            # AgentOutput (typed as Optional[Dict[str, Any]]). __get_response_json
            # checks isinstance(structured, dict) and falls back on anything else.
            return AgentOutput(
                response=ChatMessage(content="Test answer"),
                current_agent_name="TestAgent",
                structured_response=None,
            )

    return ReActAgentMock()


class ContextMock(Context):
    def __init__(self: Self):
        pass

    @classmethod
    def from_dict(cls, workflow, data, serializer=None):
        pass
