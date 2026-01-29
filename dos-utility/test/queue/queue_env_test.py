import pytest

from dos_utility.queue.env import QueueType, QueueSettings, get_queue_settings


@pytest.mark.parametrize(
    "queue_type",
    [
        "sqs",
        "redis"
    ],
)
def test_get_queue_settings(monkeypatch: pytest.MonkeyPatch, queue_type: str) -> None:
    get_queue_settings.cache_clear()

    monkeypatch.setenv("QUEUE_TYPE", queue_type)

    settings: QueueSettings = get_queue_settings()

    assert settings.queue_type is QueueType(value=queue_type)