"""Tests for the ragas-backed Evaluator.

These pin two things the worker depends on:
- Construction wires the provider SDKs together (genai.Client → instructor
  → InstructorLLM, plus the embedding factory) without touching the network.
- `evaluate()` returns the three score keys (`relevancy`, `faithfulness`,
  `utilization`) that `task.process_task` writes back to DynamoDB; a missing
  key would silently produce broken evaluation records.
"""

from dataclasses import dataclass
from typing import Any, List

import pytest

import evaluator as evaluator_module
from evaluator import Evaluator


@dataclass
class _EvalSettings:
    provider: str = "google"
    model_api_key: str = "fake-key"
    model_id: str = "gemini-x"
    temperature: float = 0.1
    embed_model_id: str = "embed-x"


class _FakeClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key


class _FakeAsyncInstructor:
    def __init__(self, client: Any) -> None:
        self.client = client


class _FakeInstructorLLM:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs


class _FakeEmbedding:
    def __init__(self, provider: str, **kwargs: Any) -> None:
        self.provider = provider
        self.kwargs = kwargs


class _ScoreResult:
    def __init__(self, value: float) -> None:
        self.value = value


class _Scorer:
    def __init__(self, value: float) -> None:
        self._value = value
        self.calls: List[dict] = []

    async def ascore(self, **kwargs: Any) -> _ScoreResult:
        self.calls.append(kwargs)
        return _ScoreResult(self._value)


def _patch_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    import google.genai as genai_mod

    monkeypatch.setattr(genai_mod, "Client", _FakeClient)
    monkeypatch.setattr(
        evaluator_module.instructor,
        "from_genai",
        lambda client, use_async: _FakeAsyncInstructor(client),
    )
    monkeypatch.setattr(evaluator_module, "InstructorLLM", _FakeInstructorLLM)
    monkeypatch.setattr(
        evaluator_module,
        "embedding_factory",
        lambda provider, **kwargs: _FakeEmbedding(provider, **kwargs),
    )


def test_evaluator_init_wires_provider_sdk(monkeypatch: pytest.MonkeyPatch):
    _patch_sdk(monkeypatch)

    ev = Evaluator(_EvalSettings())

    assert isinstance(ev.llm, _FakeInstructorLLM)
    assert ev.llm.kwargs["model"] == "gemini-x"
    assert ev.llm.kwargs["provider"] == "google"
    assert ev.llm.kwargs["temperature"] == 0.1
    assert isinstance(ev.llm.kwargs["client"], _FakeAsyncInstructor)
    assert isinstance(ev.embedding, _FakeEmbedding)
    assert ev.embedding.provider == "google"
    assert ev.embedding.kwargs["model"] == "embed-x"


@pytest.mark.asyncio
async def test_evaluate_returns_all_three_scores(monkeypatch: pytest.MonkeyPatch):
    _patch_sdk(monkeypatch)

    ev = Evaluator(_EvalSettings())

    monkeypatch.setattr(evaluator_module, "Faithfulness", lambda llm: _Scorer(0.8))
    monkeypatch.setattr(
        evaluator_module, "ContextUtilization", lambda llm: _Scorer(0.7)
    )
    monkeypatch.setattr(
        evaluator_module,
        "AnswerRelevancy",
        lambda llm, embeddings: _Scorer(0.9),
    )

    scores = await ev.evaluate(question="q?", answer="a.", context=["ctx-1", "ctx-2"])

    # The task layer writes these exact keys back to DynamoDB; renaming any
    # of them silently breaks downstream consumers (chatbot-api reads them).
    assert scores == {"relevancy": 0.9, "faithfulness": 0.8, "utilization": 0.7}
