import pytest

from typing import Callable

from dos_utility import auth
from dos_utility.auth import AuthInterface, get_auth_provider
from dos_utility.auth.env import get_auth_settings

from test.auth.mocks import (
    get_aws_auth_provider_mock,
    get_local_auth_provider_mock,
    get_auth_settings_aws_mock,
    get_auth_settings_local_mock,
)


@pytest.mark.parametrize("get_auth_settings_mock", [get_auth_settings_aws_mock, get_auth_settings_local_mock])
def test_auth_interface_not_instantiable(monkeypatch: pytest.MonkeyPatch, get_auth_settings_mock: Callable):
    """Test that AuthInterface cannot be instantiated directly."""
    get_auth_settings.cache_clear()

    monkeypatch.setattr(auth, "get_auth_settings", get_auth_settings_mock)

    with pytest.raises(expected_exception=TypeError):
        AuthInterface()


@pytest.mark.parametrize(
    "get_auth_settings_mock, func_to_mock, get_auth_mock",
    [
        (get_auth_settings_aws_mock, "get_aws_auth_provider", get_aws_auth_provider_mock),
        (get_auth_settings_local_mock, "get_local_auth_provider", get_local_auth_provider_mock),
    ],
)
def test_get_auth_provider(
    monkeypatch: pytest.MonkeyPatch,
    get_auth_settings_mock: Callable,
    func_to_mock: str,
    get_auth_mock: Callable,
):
    """Test that get_auth_provider returns the correct provider based on settings."""
    get_auth_settings.cache_clear()

    monkeypatch.setattr(auth, "get_auth_settings", get_auth_settings_mock)
    monkeypatch.setattr(auth, func_to_mock, get_auth_mock)

    provider: AuthInterface = get_auth_provider()

    assert isinstance(provider, AuthInterface)
