from typing import Dict, Any


class LocalAuthProviderMock:
    """Mock for LocalAuthProvider."""
    
    def get_jwks(self) -> Dict[str, Any]:
        """Return mock JWKS."""
        return {
            "keys": [
                {
                    "kid": "local-mock-key",
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
            "sub": "local-user-123",
            "email": "local@example.com",
            "name": "Local Development User",
            "cognito:username": "localuser",
            "exp": 9999999999,
            "iat": 1000000000,
            "auth_time": 1000000000,
            "token_use": "access",
            "iss": "https://local-development",
            "client_id": "local-client"
        }


def get_local_auth_provider_instance_mock() -> LocalAuthProviderMock:
    """Get a mock local auth provider instance."""
    return LocalAuthProviderMock()
