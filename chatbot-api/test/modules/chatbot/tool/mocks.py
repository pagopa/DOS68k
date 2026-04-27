from typing import ClassVar, Self
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool

from dos_utility.vector_db import VectorDBInterface

from test.modules.chatbot.mocks import GoogleGenAIEmbeddingMock


class VectorDBMock(VectorDBInterface):
    # stores_text is a Pydantic field on VectorDBInterface (a BaseModel subclass),
    # so Pydantic strips it from __dict__ and class-level access raises AttributeError.
    # Declaring it as ClassVar in the subclass keeps it as a plain class attribute,
    # which LlamaIndex can read without instantiating the class.
    stores_text: ClassVar[bool] = True

    def __init__(self: Self, **kwargs):
        pass

    def model_post_init(self: Self, **kwargs):
        pass

    @property
    def client(self: Self):
        pass

    def __aenter__(self: Self, **kwargs):
        pass

    def __aexit__(self: Self, **kwargs):
        pass

    def create_index(self: Self, **kwargs):
        pass

    def delete_index(self: Self, **kwargs):
        pass

    def get_indexes(self: Self, **kwargs):
        pass

    def put_objects(self: Self, **kwargs):
        pass

    def delete_objects(self: Self, **kwargs):
        pass

    def semantic_search(self: Self, **kwargs):
        pass

    def filter_search(self: Self, **kwargs):
        pass

    def aquery(self: Self, **kwargs):
        pass


def get_vector_db_instance_mock(**kwargs) -> VectorDBInterface:
    return VectorDBMock()


def get_vector_store_index_mock() -> VectorStoreIndex:
    return VectorStoreIndex.from_vector_store(
        VectorDBMock(), GoogleGenAIEmbeddingMock()
    )
