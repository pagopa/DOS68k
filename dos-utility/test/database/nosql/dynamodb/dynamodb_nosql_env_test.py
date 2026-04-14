import pytest

from dos_utility.database.nosql.dynamodb.env import get_dynamodb_settings, DynamoDBSettings


def test_get_dynamodb_settings(monkeypatch: pytest.MonkeyPatch):
    # Set environment variables for testing
    monkeypatch.setenv("DYNAMODB_REGION", "us-west-2")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    monkeypatch.setenv("DYNAMODB_PORT", "8000")
    monkeypatch.setenv("DYNAMODB_TABLE_PREFIX", "test_")

    settings: DynamoDBSettings = get_dynamodb_settings()

    assert settings.DYNAMODB_REGION == "us-west-2"
    assert settings.DYNAMODB_ENDPOINT_URL == "http://localhost:8000"
    assert settings.DYNAMODB_PORT == 8000
    assert settings.DYNAMODB_TABLE_PREFIX == "test_"