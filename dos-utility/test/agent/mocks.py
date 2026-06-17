from dataclasses import dataclass

from dos_utility.agent.env import AgentProvider


@dataclass
class AgentSettingsMock:
    AGENT_PROVIDER: str


def get_agent_settings_openai_mock() -> AgentSettingsMock:
    return AgentSettingsMock(AGENT_PROVIDER=AgentProvider.LLAMAINDEX_OPENAI)


def get_agent_settings_google_mock() -> AgentSettingsMock:
    return AgentSettingsMock(AGENT_PROVIDER=AgentProvider.LLAMAINDEX_GOOGLE)


def get_agent_settings_unknown_mock() -> AgentSettingsMock:
    return AgentSettingsMock(AGENT_PROVIDER="unsupported_provider")
