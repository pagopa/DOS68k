import pytest

from dos_utility.vector_db.qdrant.env import get_qdrant_vector_db_settings, QdrantVectorDBSettings

def test_get_qdrant_vector_db_settings(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setenv("QDRANT_HOST", "test_host")
    monkeypatch.setenv("QDRANT_PORT", "1234")

    settings: QdrantVectorDBSettings = get_qdrant_vector_db_settings()

    assert isinstance(settings, QdrantVectorDBSettings)
