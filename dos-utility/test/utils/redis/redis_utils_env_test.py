import pytest

from dos_utility.utils.redis.env import RedisConnectionSettings, get_redis_connection_settings


def test_get_redis_connection_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_redis_connection_settings.cache_clear()

    monkeypatch.setenv("REDIS_HOST", "test-host")
    monkeypatch.setenv("REDIS_PORT", "6380")

    settings: RedisConnectionSettings = get_redis_connection_settings()

    assert settings.REDIS_HOST == "test-host"
    assert settings.REDIS_PORT == 6380
