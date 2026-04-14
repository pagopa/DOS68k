from pathlib import Path

from src.modules.chatbot.agent.settings import get_agent_yaml_settings, AgentYamlSettings


def test_get_agent_yaml_settings():
    get_agent_yaml_settings.cache_clear()

    settings: AgentYamlSettings = get_agent_yaml_settings(file=Path(__file__).parent / "agent_test.yaml")

    assert settings.name == "TestAgent"
    assert settings.description == "This is a test description for the TestAgent"
    assert settings.system_prompt is None
    assert settings.system_header is None