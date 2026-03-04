from typing import Self, Any, Dict
from pydantic import SecretStr


class RequestsMock:
    """Mock for requests library."""
    
    @staticmethod
    def get(url: str, headers: Dict[str, str] = None) -> 'ResponseMock':
        """Mock GET request."""
        return ResponseMock()


class ResponseMock:
    """Mock HTTP response."""
    
    status_code: int = 200

    def json(self) -> Dict[str, Any]:
        """Return mock JWKS response."""
        return {
            "keys": [
                {
                    "kid": "mock-key-id",
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "n": "mock-modulus-value",
                    "e": "AQAB"
                }
            ]
        }
    
    def raise_for_status(self) -> None:
        """Mock status check."""
        pass


class RequestsUnhealthyMock:
    """Mock for requests library that raises errors."""
    
    @staticmethod
    def get(url: str, headers: Dict[str, str] = None) -> 'ResponseMock':
        """Mock GET request that raises an exception."""
        raise Exception("Simulated requests failure")


def requests_mock() -> RequestsMock:
    """Return a mock requests instance."""
    return RequestsMock()


def requests_unhealthy_mock() -> RequestsUnhealthyMock:
    """Return an unhealthy mock requests instance."""
    return RequestsUnhealthyMock()


class AWSAuthSettingsMock:
    """Mock AWS auth settings."""
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str = "http://localhost:9229"
    AWS_ACCESS_KEY_ID: str = "mock-access-key"
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr("mock-secret-key")
    AWS_COGNITO_USERPOOL_ID: str = "us-east-1_MockPoolId"
    ENVIRONMENT: str = "test"


def get_aws_auth_settings_mock() -> AWSAuthSettingsMock:
    """Get a mock AWS auth settings instance."""
    return AWSAuthSettingsMock()
