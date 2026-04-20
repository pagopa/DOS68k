import pytest

from src.modules.chatbot.env import get_chatbot_settings, ChatbotSettings


def test_get_chatbot_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_chatbot_settings.cache_clear()

    monkeypatch.setenv("provider", "google")
    monkeypatch.setenv("model_id", "google-model-id")
    monkeypatch.setenv("model_api_key", "google-model-api-key")
    monkeypatch.setenv("embed_model_id", "google-embed-model-id")

    settings: ChatbotSettings = get_chatbot_settings()

    assert settings.provider == "google"
    assert settings.model_id == "google-model-id"
    assert settings.model_api_key == "google-model-api-key"
    assert settings.embed_model_id == "google-embed-model-id"