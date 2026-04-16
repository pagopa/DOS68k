from llama_index.core import VectorStoreIndex

from src.modules.chatbot.tool.vector_index import load_index

from test.modules.chatbot.mocks import GoogleGenAIEmbeddingMock
from test.modules.chatbot.tool.mocks import VectorDBMock


def test_load_index():
    index: VectorStoreIndex = load_index(vector_db=VectorDBMock(), embed_model=GoogleGenAIEmbeddingMock())

    assert isinstance(index, VectorStoreIndex)
