from dataclasses import dataclass
from typing import Dict, Any
from dos_utility.auth import AuthInterface
from dos_utility.auth.env import AuthProvider


class MockAuthProvider(AuthInterface):
    """Mock implementation of AuthInterface for testing."""
    
    def get_jwks(self) -> Dict[str, Any]:
        """Return mock JWKS."""
        return {
            "keys": [
                {
                    "kid": "mock-key-id",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "mock-modulus",
                    "e": "AQAB"
                }
            ]
        }
    
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Return mock JWT claims."""
        return {
            "sub": "mock-user-id",
            "email": "mock@example.com",
            "cognito:groups": ["mock-group"]
        }


class MockAWSAuthProvider(MockAuthProvider):
    """Mock AWS/Cognito auth provider."""
    pass


class MockLocalAuthProvider(MockAuthProvider):
    """Mock local auth provider."""
    pass


def get_aws_auth_provider_mock() -> MockAWSAuthProvider:
    """Get a mock AWS auth provider instance."""
    return MockAWSAuthProvider()


def get_local_auth_provider_mock() -> MockLocalAuthProvider:
    """Get a mock local auth provider instance."""
    return MockLocalAuthProvider()


@dataclass
class AuthSettingsMock:
    """Mock auth settings."""
    AUTH_PROVIDER: str


def get_auth_settings_aws_mock() -> AuthSettingsMock:
    """Get mock auth settings for AWS provider."""
    return AuthSettingsMock(AUTH_PROVIDER=AuthProvider.AWS)


def get_auth_settings_local_mock() -> AuthSettingsMock:
    """Get mock auth settings for local provider."""
    return AuthSettingsMock(AUTH_PROVIDER=AuthProvider.LOCAL)
