from pathlib import Path

from src.modules.chatbot.tool.settings import get_yaml_settings, YamlSettings

def test_get_yaml_settings():
    get_yaml_settings.cache_clear()

    settings: YamlSettings = get_yaml_settings(file=Path(__file__).parent / "tool_config_folder" / "RAGToolTest.yaml")

    assert settings.index_id == "index-test"
    assert settings.name == "RAGToolTest"
    assert settings.description == "Test RAG tool description"
