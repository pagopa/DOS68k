import pytest

from src.worker import embedder
from src.worker.embedder import Embedder, get_embedder
from src.worker.parsers import ChunkData
from dos_utility.vector_db import ObjectData

from test.worker.mocks import EmbedModelMock


def test_embedder_transform(monkeypatch):
    monkeypatch.setattr(embedder, "get_embed_model", lambda **kwargs: EmbedModelMock())

    e = Embedder(
        provider="google",
        embed_model_id="text-embedding-004",
        embed_batch_size=100,
        embed_dim=3,
        embed_task="RETRIEVAL_DOCUMENT",
        embed_retries=3,
        embed_retry_min_seconds=1.0,
        model_api_key="test-key",
    )
    chunks = [
        ChunkData(filename="doc.pdf", chunk_id=0, content="hello"),
        ChunkData(filename="doc.pdf", chunk_id=1, content="world"),
    ]

    result = e.transform(chunks=chunks)

    assert len(result) == 2
    assert all(isinstance(o, ObjectData) for o in result)
    assert result[0].filename == "doc.pdf"
    assert result[0].chunk_id == 0
    assert result[0].content == "hello"
    assert result[0].vector == [0.1, 0.2, 0.3]
    assert result[1].chunk_id == 1
    assert result[1].content == "world"


def test_get_embedder(monkeypatch):
    monkeypatch.setattr(embedder, "get_embed_model", lambda **kwargs: EmbedModelMock())
    get_embedder.cache_clear()

    e = get_embedder(
        provider="google",
        embed_model_id="text-embedding-004",
        embed_batch_size=100,
        embed_dim=3,
        embed_task="RETRIEVAL_DOCUMENT",
        embed_retries=3,
        embed_retry_min_seconds=1.0,
        model_api_key="test-key",
    )

    assert isinstance(e, Embedder)
    get_embedder.cache_clear()
