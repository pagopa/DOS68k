"""Tests for `dos_utility.tracing.instrumentation`.

Verify install/uninstall of the LlamaIndex OpenInference instrumentation:
- a small LlamaIndex op under installed instrumentation produces Spans on
  an `InMemorySpanExporter` carrying OpenInference-shaped attributes;
- after uninstall, the same op produces no further Spans.
"""

import pytest

from llama_index.core.llms.mock import MockLLM
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from dos_utility.tracing.instrumentation import (
    install_llamaindex_instrumentation,
    uninstall_llamaindex_instrumentation,
)


@pytest.fixture
def exporter_provider():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    prev = otel_trace.get_tracer_provider()
    otel_trace._TRACER_PROVIDER_SET_ONCE._done = False  # type: ignore[attr-defined]
    otel_trace.set_tracer_provider(provider)
    try:
        yield provider, exporter
    finally:
        # Be defensive: always remove instrumentation between tests so a
        # failure does not leak global state into the next test.
        uninstall_llamaindex_instrumentation()
        otel_trace._TRACER_PROVIDER_SET_ONCE._done = False  # type: ignore[attr-defined]
        otel_trace.set_tracer_provider(prev)


def test_install_emits_openinference_spans(exporter_provider):
    provider, exporter = exporter_provider

    install_llamaindex_instrumentation(tracer_provider=provider)

    llm = MockLLM(max_tokens=5)
    llm.complete("hello world")

    spans = exporter.get_finished_spans()
    assert len(spans) >= 1
    attrs = dict(spans[0].attributes or {})
    # OpenInference semantic-convention attributes that should be present
    # on an LLM completion span.
    assert "llm.model_name" in attrs
    assert "input.value" in attrs


def test_uninstall_stops_span_emission(exporter_provider):
    provider, exporter = exporter_provider

    install_llamaindex_instrumentation(tracer_provider=provider)
    MockLLM(max_tokens=5).complete("warmup")
    assert len(exporter.get_finished_spans()) >= 1

    exporter.clear()
    uninstall_llamaindex_instrumentation()

    MockLLM(max_tokens=5).complete("after uninstall")
    assert len(exporter.get_finished_spans()) == 0


def test_reinstall_after_uninstall_is_clean(exporter_provider):
    provider, exporter = exporter_provider

    install_llamaindex_instrumentation(tracer_provider=provider)
    uninstall_llamaindex_instrumentation()
    install_llamaindex_instrumentation(tracer_provider=provider)

    MockLLM(max_tokens=5).complete("hello")

    assert len(exporter.get_finished_spans()) >= 1
