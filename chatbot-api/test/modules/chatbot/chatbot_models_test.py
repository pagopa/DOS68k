import pytest
import llama_index.llms.google_genai
import llama_index.embeddings.google_genai

from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding

from src.modules.chatbot.models import get_llm, get_embed_model

from test.modules.chatbot.mocks import GoogleGenAIMock, GoogleGenAIEmbeddingMock

def test_get_llm_google_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(llama_index.llms.google_genai, "GoogleGenAI", GoogleGenAIMock)

    model: LLM = get_llm(
        provider="google",
        model_id="gemini-2.5-flash-lite",
        temperature=1.0,
        max_tokens=1024,
        api_key="my-api-key",
    )

    assert isinstance(model, LLM)

def test_get_embed_model_google_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(llama_index.embeddings.google_genai, "GoogleGenAIEmbedding", GoogleGenAIEmbeddingMock)

    embedding_model: BaseEmbedding = get_embed_model(
        provider="google",
        model_id="gemini-embedding-001",
        embed_batch_size=100,
        embed_dim=768,
        task_type="RETRIEVAL_QUERY",
        retries=3,
        retry_min_seconds=1.0,
        api_key="my-api-key",
    )

    assert isinstance(embedding_model, BaseEmbedding)
