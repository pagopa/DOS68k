from llama_index.core.tools import QueryEngineTool

from src.modules.chatbot.tool.factory import get_query_engine_tool

from test.modules.chatbot.mocks import GoogleGenAIEmbeddingMock, GoogleGenAIMock
from test.modules.chatbot.tool.mocks import get_vector_store_index_mock


def test_get_query_engine_tool():
    tool: QueryEngineTool = get_query_engine_tool(
        index=get_vector_store_index_mock(),
        name="test tool",
        description="test description",
        llm=GoogleGenAIMock(),
        embed_model=GoogleGenAIEmbeddingMock(),
    )

    assert isinstance(tool, QueryEngineTool)
