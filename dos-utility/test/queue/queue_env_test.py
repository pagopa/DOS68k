import pytest

from dos_utility.queue.env import QueueProvider, QueueSettings, get_queue_settings


@pytest.mark.parametrize(
    "queue_provider",
    [
        "sqs",
        "redis"
    ],
)
def test_get_queue_settings(monkeypatch: pytest.MonkeyPatch, queue_provider: str) -> None:
    get_queue_settings.cache_clear()

    monkeypatch.setenv("QUEUE_PROVIDER", queue_provider)

    settings: QueueSettings = get_queue_settings()

    assert settings.QUEUE_PROVIDER is QueueProvider(value=queue_provider)