import pytest
import llama_index.embeddings.google_genai as ggai

from src.worker import models
from test.worker.mocks import GoogleGenAIEmbeddingMock


def test_get_embed_model_google(monkeypatch):
    monkeypatch.setattr(ggai, "GoogleGenAIEmbedding", GoogleGenAIEmbeddingMock)

    result = models.get_embed_model(
        provider="google",
        model_id="gemini-embedding-001",
        embed_batch_size=100,
        embed_dim=768,
        task_type="RETRIEVAL_DOCUMENT",
        retries=3,
        retry_min_seconds=1.0,
        api_key="test-key",
    )

    assert isinstance(result, GoogleGenAIEmbeddingMock)
    assert result.kwargs["model_name"] == "gemini-embedding-001"
    assert result.kwargs["api_key"] == "test-key"
    assert result.kwargs["embed_batch_size"] == 100
    assert result.kwargs["retries"] == 3
    assert result.kwargs["retry_min_seconds"] == 1.0
