import pytest

from dos_utility.database.nosql.env import (
    NoSQLProvider,
    NoSQLSettings,
    get_nosql_settings,
)


@pytest.mark.parametrize(
    "nosql_provider", [provider.value for provider in NoSQLProvider]
)
def test_get_nosql_settings(
    monkeypatch: pytest.MonkeyPatch, nosql_provider: str
) -> None:
    get_nosql_settings.cache_clear()

    monkeypatch.setenv("NOSQL_PROVIDER", nosql_provider)

    settings: NoSQLSettings = get_nosql_settings()

    assert settings.NOSQL_PROVIDER is NoSQLProvider(value=nosql_provider)
