import pytest

from dos_utility.tracing.env import get_tracing_settings, TracingProvider


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_tracing_settings.cache_clear()
    yield
    get_tracing_settings.cache_clear()


def test_default_provider_is_noop(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TRACING_PROVIDER", raising=False)
    settings = get_tracing_settings()
    assert settings.TRACING_PROVIDER is TracingProvider.NOOP


def test_provider_overrideable_via_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TRACING_PROVIDER", "langfuse")
    settings = get_tracing_settings()
    assert settings.TRACING_PROVIDER is TracingProvider.LANGFUSE
