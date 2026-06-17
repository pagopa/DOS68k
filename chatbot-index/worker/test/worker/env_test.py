import pytest

from src.worker import env
from src.worker.env import TaskSettings, GlobalSettings, StorageSettings


def test_get_task_settings(monkeypatch):
    monkeypatch.setenv("PROVIDER", "google")
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    monkeypatch.setenv("EMBED_CHUNK_SIZE", "512")
    monkeypatch.setenv("EMBED_CHUNK_OVERLAP", "50")
    monkeypatch.setenv("EMBED_MODEL_ID", "gemini-embedding-001")
    env.get_task_settings.cache_clear()

    settings = env.get_task_settings()

    assert isinstance(settings, TaskSettings)
    assert settings.provider == "google"
    assert settings.model_api_key == "test-key"
    assert settings.embed_chunk_size == 512
    assert settings.embed_chunk_overlap == 50
    assert settings.embed_model_id == "gemini-embedding-001"
    env.get_task_settings.cache_clear()


def test_get_global_settings():
    env.get_global_settings.cache_clear()

    settings = env.get_global_settings()

    assert isinstance(settings, GlobalSettings)
    assert settings.log_level == 20
    env.get_global_settings.cache_clear()


def test_get_storage_settings(monkeypatch):
    monkeypatch.setenv("INDEX_DOCUMENTS_BUCKET_NAME", "test-bucket")
    env.get_storage_settings.cache_clear()

    settings = env.get_storage_settings()

    assert isinstance(settings, StorageSettings)
    assert settings.index_documents_bucket_name == "test-bucket"
    env.get_storage_settings.cache_clear()
