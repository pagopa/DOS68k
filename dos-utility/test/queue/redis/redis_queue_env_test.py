import pytest

from dos_utility.queue.redis.env import RedisQueueSettings, get_redis_queue_settings


def test_get_redis_queue_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_redis_queue_settings.cache_clear()

    monkeypatch.setenv("REDIS_STREAM", "test-stream")
    monkeypatch.setenv("REDIS_GROUP", "test-group")

    settings: RedisQueueSettings = get_redis_queue_settings()

    assert settings.REDIS_STREAM == "test-stream"
    assert settings.REDIS_GROUP == "test-group"
