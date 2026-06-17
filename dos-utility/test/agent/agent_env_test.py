import pytest

from dos_utility.agent.env import AgentProvider, AgentSettings, get_agent_settings


@pytest.mark.parametrize(
    "provider",
    ["llamaindex_google", "llamaindex_openai"],
)
def test_get_agent_settings(monkeypatch: pytest.MonkeyPatch, provider: str) -> None:
    get_agent_settings.cache_clear()

    monkeypatch.setenv("AGENT_PROVIDER", provider)

    settings: AgentSettings = get_agent_settings()

    assert settings.AGENT_PROVIDER is AgentProvider(provider)

    get_agent_settings.cache_clear()


def test_agent_provider_enum_values():
    assert AgentProvider.LLAMAINDEX_GOOGLE == "llamaindex_google"
    assert AgentProvider.LLAMAINDEX_OPENAI == "llamaindex_openai"
