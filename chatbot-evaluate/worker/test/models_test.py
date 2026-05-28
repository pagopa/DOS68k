"""Tests for the LLM/embedding provider factories.

Locks down the contract that `task.process_task` relies on: given a provider
and settings, return an object configured with exactly those settings. Any
silent drift in argument names breaks the worker at startup.
"""

from typing import Any, Dict

import pytest

from src.worker import models


class _Recorder:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs: Dict[str, Any] = kwargs


def test_get_llm_google_passes_settings_through(monkeypatch: pytest.MonkeyPatch):
    import llama_index.llms.google_genai as google_llm_mod

    monkeypatch.setattr(google_llm_mod, "GoogleGenAI", _Recorder)

    llm = models.get_llm(
        provider="google",
        model_id="gemini-x",
        temperature=0.25,
        max_tokens=512,
        api_key="key-123",
    )

    assert isinstance(llm, _Recorder)
    assert llm.kwargs["model"] == "gemini-x"
    assert llm.kwargs["temperature"] == 0.25
    assert llm.kwargs["max_tokens"] == 512
    assert llm.kwargs["api_key"] == "key-123"
    # Safety settings must be wired so harmful content is filtered out;
    # a regression that drops this would silently weaken the evaluator.
    assert llm.kwargs["generation_config"] is not None


def test_get_embed_model_google_passes_settings_through(
    monkeypatch: pytest.MonkeyPatch,
):
    import llama_index.embeddings.google_genai as google_embed_mod

    monkeypatch.setattr(google_embed_mod, "GoogleGenAIEmbedding", _Recorder)

    embed = models.get_embed_model(
        provider="google",
        model_id="embed-x",
        embed_batch_size=50,
        embed_dim=128,
        task_type="RETRIEVAL_DOCUMENT",
        retries=2,
        retry_min_seconds=0.5,
        api_key="key-abc",
    )

    assert isinstance(embed, _Recorder)
    assert embed.kwargs["model_name"] == "embed-x"
    assert embed.kwargs["api_key"] == "key-abc"
    assert embed.kwargs["embed_batch_size"] == 50
    assert embed.kwargs["retries"] == 2
    assert embed.kwargs["retry_min_seconds"] == 0.5
    # embedding_config bundles dim + task_type — the worker writes vectors
    # at this exact dimensionality into the store, so a mismatch corrupts
    # the index. Assert the wiring is preserved.
    assert embed.kwargs["embedding_config"].output_dimensionality == 128
    assert embed.kwargs["embedding_config"].task_type == "RETRIEVAL_DOCUMENT"
