import pytest

from src.dos_utility.queue.sqs.env import SQSQueueSettings, get_sqs_queue_settings


def test_get_sqs_queue_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setenv("SQS_ENDPOINT_URL", "http://test-endpoint")
    monkeypatch.setenv("SQS_PORT", "1234")
    monkeypatch.setenv("SQS_REGION", "eu-west-1")
    monkeypatch.setenv("SQS_AWS_ACCESS_KEY_ID", "my-access-key")
    monkeypatch.setenv("SQS_AWS_SECRET_ACCESS_KEY", "my-secret-key")
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    settings: SQSQueueSettings = get_sqs_queue_settings()

    assert settings.SQS_ENDPOINT_URL == "http://test-endpoint"
    assert settings.SQS_PORT == 1234
    assert settings.SQS_REGION == "eu-west-1"
    assert settings.SQS_AWS_ACCESS_KEY_ID == "my-access-key"
    assert settings.SQS_AWS_SECRET_ACCESS_KEY.get_secret_value() == "my-secret-key"
    assert settings.SQS_QUEUE_NAME == "my-queue"
    assert settings.SQS_QUEUE_URL == "http://test-queue-url"