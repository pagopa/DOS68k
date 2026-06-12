from pathlib import Path

import pytest

from src.modules.chatbot.env import ChatbotSettings, get_chatbot_settings


def test_get_chatbot_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    get_chatbot_settings.cache_clear()
    monkeypatch.delenv("TOOLS_CONFIG_DIR", raising=False)
    monkeypatch.delenv("AGENT_CONFIG_PATH", raising=False)

    settings: ChatbotSettings = get_chatbot_settings()

    assert isinstance(settings.tools_config_dir, Path)
    assert settings.tools_config_dir.name == "config"
    assert isinstance(settings.agent_config_path, Path)
    assert settings.agent_config_path.name == "agent.yaml"


def test_get_chatbot_settings_overrides(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    get_chatbot_settings.cache_clear()
    custom_dir: Path = tmp_path / "tools"
    custom_dir.mkdir()
    custom_agent: Path = tmp_path / "agent.yaml"
    custom_agent.write_text("name: X\ndescription: Y\n")

    monkeypatch.setenv("TOOLS_CONFIG_DIR", str(custom_dir))
    monkeypatch.setenv("AGENT_CONFIG_PATH", str(custom_agent))

    settings: ChatbotSettings = get_chatbot_settings()

    assert settings.tools_config_dir == custom_dir
    assert settings.agent_config_path == custom_agent
