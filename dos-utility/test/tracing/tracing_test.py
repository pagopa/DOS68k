import pytest

from typing import Callable

from dos_utility import tracing
from dos_utility.tracing import TracingInterface, get_tracer
from dos_utility.tracing.env import get_tracing_settings

from test.tracing.mocks import get_tracing_settings_noop_mock


# ---------------------------------------------------------------------------
# TracingInterface is not directly instantiable
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracing_interface_not_instantiable():
    with pytest.raises(TypeError):
        async with TracingInterface():
            pass


# ---------------------------------------------------------------------------
# NOOP provider — lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_tracing_settings_mock",
    [get_tracing_settings_noop_mock],
)
async def test_get_tracer_returns_tracing_interface(
    monkeypatch: pytest.MonkeyPatch,
    get_tracing_settings_mock: Callable,
):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_mock)

    tracer = get_tracer()
    assert isinstance(tracer, TracingInterface)

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_noop_tracer_is_healthy(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_noop_mock)

    tracer = get_tracer()
    async with tracer:
        assert await tracer.is_healthy() is True

    get_tracer.cache_clear()


# ---------------------------------------------------------------------------
# NOOP provider — trace handle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_noop_tracer_trace_returns_non_empty_id(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_noop_mock)

    tracer = get_tracer()
    async with tracer:
        async with tracer.trace(
            name="test",
            session_id="session-1",
            user_id="user-1",
            input="hello",
        ) as handle:
            assert isinstance(handle.id, str)
            assert len(handle.id) > 0

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_noop_tracer_set_output_and_metadata_do_not_raise(
    monkeypatch: pytest.MonkeyPatch,
):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_noop_mock)

    tracer = get_tracer()
    async with tracer:
        async with tracer.trace(
            name="test", session_id="s", user_id="u", input="q"
        ) as handle:
            handle.set_output("some answer")
            handle.set_metadata({"key": "val"})
            await handle.add_span(name="llm_generation", input="q", output="a")

    get_tracer.cache_clear()


# ---------------------------------------------------------------------------
# NOOP provider — score and flush
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_noop_tracer_score_does_not_raise(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_noop_mock)

    tracer = get_tracer()
    async with tracer:
        await tracer.score(trace_id="some-id", name="faithfulness", value=0.9)

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_noop_tracer_flush_does_not_raise(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    monkeypatch.setattr(tracing, "get_tracing_settings", get_tracing_settings_noop_mock)

    tracer = get_tracer()
    async with tracer:
        await tracer.flush(timeout=1.0)

    get_tracer.cache_clear()
