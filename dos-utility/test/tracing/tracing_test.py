import pytest

from typing import Callable

from dos_utility import tracing
from dos_utility.tracing import TracingInterface, get_tracer
from dos_utility.tracing.env import get_tracing_settings

from test.tracing.mocks import (
    get_tracing_settings_noop_mock,
    get_tracing_settings_langfuse_mock,
)


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


# ---------------------------------------------------------------------------
# Langfuse provider — shared fakes
# ---------------------------------------------------------------------------

from contextlib import contextmanager


@contextmanager
def _fake_propagate_attributes(**kwargs):
    yield


class _FakeLangfuse:
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.start_observation_calls = []
        self.set_trace_io_calls = []
        self.create_score_calls = []
        self.flush_calls = []
        self._healthy = True
        self._trace_id = "fake-trace-id"

    @contextmanager
    def start_as_current_observation(
        self, *, name, input=None, output=None, metadata=None, **kwargs
    ):
        self.start_observation_calls.append(
            {"name": name, "input": input, "output": output, "metadata": metadata}
        )
        yield self

    def get_current_trace_id(self) -> str:
        return self._trace_id

    def set_current_trace_io(self, *, input=None, output=None):
        self.set_trace_io_calls.append({"input": input, "output": output})

    def create_score(self, **kwargs):
        self.create_score_calls.append(kwargs)

    def flush(self):
        self.flush_calls.append(True)

    def auth_check(self) -> bool:
        if not self._healthy:
            raise RuntimeError("unreachable")
        return True


# ---------------------------------------------------------------------------
# Langfuse provider — lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_langfuse_tracer_returns_tracing_interface(
    monkeypatch: pytest.MonkeyPatch,
):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", _FakeLangfuse)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        assert isinstance(tracer, TracingInterface)

    get_tracer.cache_clear()


# ---------------------------------------------------------------------------
# Langfuse provider — trace handle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_langfuse_tracer_trace_returns_non_empty_id(
    monkeypatch: pytest.MonkeyPatch,
):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", _FakeLangfuse)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        async with tracer.trace(
            name="test", session_id="s", user_id="u", input="q"
        ) as handle:
            assert isinstance(handle.id, str)
            assert len(handle.id) > 0

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_langfuse_tracer_output_reaches_sdk(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        async with tracer.trace(name="test") as handle:
            handle.set_output("answer")

    assert any(c.get("output") == "answer" for c in fake_lf.set_trace_io_calls)

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_langfuse_tracer_span_reaches_sdk(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        async with tracer.trace(name="test") as handle:
            await handle.add_span(name="llm_generation", input="q", output="a")

    assert any(
        c.get("name") == "llm_generation" for c in fake_lf.start_observation_calls
    )

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_langfuse_tracer_exception_in_body_still_closes_trace(
    monkeypatch: pytest.MonkeyPatch,
):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        with pytest.raises(ValueError):
            async with tracer.trace(name="test") as handle:
                handle.set_output("partial")
                raise ValueError("boom")

    assert any(c.get("output") == "partial" for c in fake_lf.set_trace_io_calls)

    get_tracer.cache_clear()


# ---------------------------------------------------------------------------
# Langfuse provider — score and flush
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_langfuse_tracer_score_calls_sdk(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        await tracer.score(trace_id="tid", name="faithfulness", value=0.9)

    assert len(fake_lf.create_score_calls) == 1
    call = fake_lf.create_score_calls[0]
    assert call["trace_id"] == "tid"
    assert call["name"] == "faithfulness"
    assert call["value"] == 0.9

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_langfuse_tracer_flush_calls_sdk(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        await tracer.flush()

    assert len(fake_lf.flush_calls) >= 1

    get_tracer.cache_clear()


# ---------------------------------------------------------------------------
# Langfuse provider — health check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_langfuse_tracer_is_healthy_true(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        assert await tracer.is_healthy() is True

    get_tracer.cache_clear()


@pytest.mark.asyncio
async def test_langfuse_tracer_is_healthy_false(monkeypatch: pytest.MonkeyPatch):
    get_tracing_settings.cache_clear()
    get_tracer.cache_clear()

    import dos_utility.tracing.langfuse.implementation as langfuse_impl

    fake_lf = _FakeLangfuse()
    fake_lf._healthy = False
    monkeypatch.setattr(
        tracing, "get_tracing_settings", get_tracing_settings_langfuse_mock
    )
    monkeypatch.setattr(langfuse_impl, "Langfuse", lambda **kw: fake_lf)
    monkeypatch.setattr(
        langfuse_impl, "propagate_attributes", _fake_propagate_attributes
    )

    tracer = get_tracer()
    async with tracer:
        assert await tracer.is_healthy() is False

    get_tracer.cache_clear()
