import pytest

from dos_utility.vector_db.env import get_vector_db_settings, VectorDBProvider, VectorDBSettings


@pytest.mark.parametrize(
    "env_value, expected_provider",
    [
        ("redis", VectorDBProvider.REDIS),
        ("qdrant", VectorDBProvider.QDRANT),
    ],
)
def test_get_vector_db_settings(monkeypatch: pytest.MonkeyPatch, env_value: str, expected_provider: VectorDBProvider) -> None:
    get_vector_db_settings.cache_clear()

    monkeypatch.setenv("VECTOR_DB_PROVIDER", env_value)

    settings: VectorDBSettings = get_vector_db_settings()

    assert settings.VECTOR_DB_PROVIDER is expected_provider
