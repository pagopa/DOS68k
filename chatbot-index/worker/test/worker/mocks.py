from contextlib import asynccontextmanager
from typing import Self, Optional, List, Tuple

from dos_utility.vector_db import SearchResult


# ─────────────────────────────────────────────────────────────────────────────
# Settings mocks
# ─────────────────────────────────────────────────────────────────────────────


class GlobalSettingsMock:
    log_level = 20


class TaskSettingsMock:
    provider = "google"
    model_api_key = "test-key"
    embed_chunk_size = 512
    embed_chunk_overlap = 50
    embed_model_id = "gemini-embedding-001"
    embed_batch_size = 100
    embed_dim = 768
    embed_task = "RETRIEVAL_DOCUMENT"
    embed_retries = 3
    embed_retry_min_seconds = 1.0


class StorageSettingsMock:
    index_documents_bucket_name = "test-bucket"


# ─────────────────────────────────────────────────────────────────────────────
# Logger mock
# ─────────────────────────────────────────────────────────────────────────────


class LoggerMock:
    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Queue mocks
# ─────────────────────────────────────────────────────────────────────────────


class QueueClientMock:
    def __init__(
        self: Self, messages: List[Optional[bytes]], ack_tokens: List[Optional[str]]
    ):
        self._messages = messages
        self._ack_tokens = ack_tokens
        self._index = 0
        self.acknowledged: List[str] = []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, *_) -> None:
        pass

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        if self._index < len(self._messages):
            msg = self._messages[self._index]
            ack = self._ack_tokens[self._index]
            self._index += 1
            return msg, ack
        raise SystemExit("test complete")

    async def acknowledge(self: Self, ack_token: str) -> None:
        self.acknowledged.append(ack_token)


def make_queue_client_ctx_mock(client: QueueClientMock):
    @asynccontextmanager
    async def ctx_mock():
        yield client

    return ctx_mock


# ─────────────────────────────────────────────────────────────────────────────
# VectorDB mock
# ─────────────────────────────────────────────────────────────────────────────


class VectorDBMock:
    def __init__(
        self: Self,
        indexes: Optional[List[str]] = None,
        filter_results: Optional[List[SearchResult]] = None,
    ):
        self._indexes = indexes or []
        self._filter_results = filter_results or []
        self.create_index_calls: List[dict] = []
        self.put_calls: List[dict] = []
        self.delete_calls: List[dict] = []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, *_) -> None:
        pass

    async def get_indexes(self: Self) -> List[str]:
        return list(self._indexes)

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        self.create_index_calls.append(
            {"index_name": index_name, "vector_dim": vector_dim}
        )

    async def filter_search(
        self: Self, index_name: str, filters, max_results: int
    ) -> List:
        return self._filter_results

    async def put_objects(self: Self, index_name: str, data: list) -> None:
        self.put_calls.append({"index_name": index_name, "data": data})

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        self.delete_calls.append({"index_name": index_name, "ids": ids})


def make_vector_db_ctx_mock(vdb: VectorDBMock):
    @asynccontextmanager
    async def ctx_mock(**kwargs):
        yield vdb

    return ctx_mock


# ─────────────────────────────────────────────────────────────────────────────
# Storage mock
# ─────────────────────────────────────────────────────────────────────────────


class StorageMock:
    def __init__(self: Self, data: bytes = b"test content"):
        self._data = data

    def get_object(self: Self, bucket: str, name: str) -> bytes:
        return self._data


# ─────────────────────────────────────────────────────────────────────────────
# Embed model mock
# ─────────────────────────────────────────────────────────────────────────────


class EmbedModelMock:
    def get_text_embedding(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3]


# ─────────────────────────────────────────────────────────────────────────────
# SentenceSplitter mock
# ─────────────────────────────────────────────────────────────────────────────


class TextNodeMock:
    def __init__(self, text: str):
        self.text = text


class SentenceSplitterMock:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def __call__(self, documents) -> List[TextNodeMock]:
        return [TextNodeMock(text="chunk 1"), TextNodeMock(text="chunk 2")]


# ─────────────────────────────────────────────────────────────────────────────
# pymupdf mock
# ─────────────────────────────────────────────────────────────────────────────


class PyMuPDFPageMock:
    def get_text(self) -> str:
        return "page content"


class PyMuPDFDocumentMock:
    page_count = 2

    def load_page(self, number: int) -> PyMuPDFPageMock:
        return PyMuPDFPageMock()


class PyMuPDFMock:
    def open(self, stream) -> PyMuPDFDocumentMock:
        return PyMuPDFDocumentMock()


# ─────────────────────────────────────────────────────────────────────────────
# GoogleGenAIEmbedding mock
# ─────────────────────────────────────────────────────────────────────────────


class GoogleGenAIEmbeddingMock:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
