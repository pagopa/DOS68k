"""
Test per l'adaptive authentication layer.
Dimostra come testare i provider di autenticazione con mock.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from src.service.auth_provider_base import BaseAuthProvider
from src.service import get_provider


class MockAuthProvider(BaseAuthProvider):
    """Mock provider per i test."""
    
    def get_jwks(self):
        return {
            "keys": [
                {
                    "kid": "test-key-id",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "test-n",
                    "e": "AQAB"
                }
            ]
        }
    
    def verify_jwt(self, token: str):
        if token == "valid-token":
            return {
                "sub": "test-user-123",
                "email": "test@example.com",
                "exp": 9999999999
            }
        elif token == "expired-token":
            raise HTTPException(status_code=401, detail="Token has expired")
        else:
            raise HTTPException(status_code=401, detail="Invalid token")


class TestGetProvider:
    """Test per la funzione get_provider."""
    
    def test_create_cognito_provider(self):
        """Test creazione provider Cognito."""
        with patch('src.service.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "cognito"
            mock_settings.aws_region = "us-east-1"
            mock_settings.auth_cognito_userpool_id = "test-pool"
            mock_settings.environment = "test"
            mock_settings.aws_endpoint_url = "http://localhost:4566"
            
            provider = get_provider()
            assert provider.__class__.__name__ == "CognitoAuthProvider"
    
    def test_create_keycloak_provider(self):
        """Test creazione provider Keycloak."""
        with patch('src.service.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "keycloak"
            mock_settings.keycloak_url = "http://keycloak:8080"
            mock_settings.keycloak_realm = "test-realm"
            
            provider = get_provider()
            assert provider.__class__.__name__ == "KeycloakAuthProvider"
    
    def test_create_local_provider(self):
        """Test creazione provider Local."""
        with patch('src.service.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "local"
            
            provider = get_provider()
            assert provider.__class__.__name__ == "LocalAuthProvider"
    
    def test_unsupported_provider(self):
        """Test provider non supportato."""
        with patch('src.service.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "unsupported"
            
            with pytest.raises(ValueError) as exc_info:
                get_provider()
            
            assert "Unsupported auth provider" in str(exc_info.value)


class TestMockAuthProvider:
    """Test usando un mock provider."""
    
    def test_verify_valid_token(self):
        """Test verifica di un token valido."""
        mock_provider = MockAuthProvider()
        claims = mock_provider.verify_jwt("valid-token")
        
        assert claims["sub"] == "test-user-123"
        assert claims["email"] == "test@example.com"
        assert claims["exp"] == 9999999999
    
    def test_verify_expired_token(self):
        """Test verifica di un token scaduto."""
        mock_provider = MockAuthProvider()
        
        with pytest.raises(HTTPException) as exc_info:
            mock_provider.verify_jwt("expired-token")
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_invalid_token(self):
        """Test verifica di un token non valido."""
        mock_provider = MockAuthProvider()
        
        with pytest.raises(HTTPException) as exc_info:
            mock_provider.verify_jwt("invalid-token")
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
    
    def test_get_jwks(self):
        """Test recupero delle chiavi pubbliche."""
        mock_provider = MockAuthProvider()
        jwks = mock_provider.get_jwks()
        
        assert "keys" in jwks
        assert len(jwks["keys"]) == 1
        assert jwks["keys"][0]["kid"] == "test-key-id"


class TestJWTCheckRouter:
    """Test per il router JWT check."""
    
    def test_jwt_check_endpoint_with_valid_token(self, client):
        """Test endpoint con token valido."""
        with patch('src.routers.jwt_check.get_provider', return_value=MockAuthProvider()):
            response = client.get(
                "/protected/jwt-check",
                headers={"Authorization": "Bearer valid-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["payload"]["sub"] == "test-user-123"
    
    def test_jwt_check_endpoint_missing_bearer(self, client):
        """Test endpoint senza Bearer prefix."""
        response = client.get(
            "/protected/jwt-check",
            headers={"Authorization": "valid-token"}
        )
        
        assert response.status_code == 401
    
    def test_jwt_check_endpoint_no_authorization(self, client):
        """Test endpoint senza header Authorization."""
        response = client.get("/protected/jwt-check")
        
        assert response.status_code == 422  # Validation error
    
    def test_jwt_check_endpoint_invalid_token(self, client):
        """Test endpoint con token non valido."""
        with patch('src.routers.jwt_check.get_provider', return_value=MockAuthProvider()):
            response = client.get(
                "/protected/jwt-check",
                headers={"Authorization": "Bearer invalid-token"}
            )
            
            assert response.status_code == 401


class TestLocalAuthProvider:
    """Test per il LocalAuthProvider."""
    
    def test_local_provider_always_succeeds(self):
        """Test che il provider local ritorna sempre successo."""
        from src.service.local_auth_provider import LocalAuthProvider
        
        provider = LocalAuthProvider()
        
        # Qualsiasi token dovrebbe funzionare
        claims = provider.verify_jwt("any-token-here")
        
        assert claims["sub"] == "local-user-123"
        assert claims["email"] == "local@example.com"
        assert "exp" in claims
    
    def test_local_provider_with_invalid_token(self):
        """Test che il provider local funziona anche con token invalidi."""
        from src.service.local_auth_provider import LocalAuthProvider
        
        provider = LocalAuthProvider()
        
        # Anche token malformati dovrebbero funzionare
        claims = provider.verify_jwt("not-even-a-jwt")
        
        assert claims["sub"] == "local-user-123"
    
    def test_local_provider_get_jwks(self):
        """Test recupero JWKS dal provider local."""
        from src.service.local_auth_provider import LocalAuthProvider
        
        provider = LocalAuthProvider()
        jwks = provider.get_jwks()
        
        assert "keys" in jwks
        assert len(jwks["keys"]) == 1
        assert jwks["keys"][0]["kid"] == "local-mock-key"
    
    def test_jwt_check_endpoint_without_auth_header_local(self, client):
        """Test che con AUTH_PROVIDER=local l'header Authorization è opzionale."""
        from src.service.local_auth_provider import LocalAuthProvider
        
        with patch('src.routers.jwt_check.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "local"
            with patch('src.routers.jwt_check.get_provider', return_value=LocalAuthProvider()):
                # Senza header Authorization dovrebbe funzionare in modalità local
                response = client.get("/protected/jwt-check")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["payload"]["sub"] == "local-user-123"
    
    def test_jwt_check_endpoint_with_auth_header_local(self, client):
        """Test che con AUTH_PROVIDER=local funziona anche con l'header."""
        from src.service.local_auth_provider import LocalAuthProvider
        
        with patch('src.routers.jwt_check.SETTINGS') as mock_settings:
            mock_settings.auth_provider = "local"
            with patch('src.routers.jwt_check.get_provider', return_value=LocalAuthProvider()):
                # Con header Authorization dovrebbe funzionare comunque
                response = client.get(
                    "/protected/jwt-check",
                    headers={"Authorization": "Bearer any-token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"


class TestMockAuthProvider:
    """Test usando un mock provider."""
    
    def test_verify_valid_token(self):
        """Test verifica di un token valido."""
        mock_provider = MockAuthProvider()
        claims = mock_provider.verify_jwt("valid-token")
        
        assert claims["sub"] == "test-user-123"
        assert claims["email"] == "test@example.com"
        assert claims["exp"] == 9999999999
    
    def test_verify_expired_token(self):
        """Test verifica di un token scaduto."""
        mock_provider = MockAuthProvider()
        
        with pytest.raises(HTTPException) as exc_info:
            mock_provider.verify_jwt("expired-token")
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_invalid_token(self):
        """Test verifica di un token non valido."""
        mock_provider = MockAuthProvider()
        
        with pytest.raises(HTTPException) as exc_info:
            mock_provider.verify_jwt("invalid-token")
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
    
    def test_get_jwks(self):
        """Test recupero delle chiavi pubbliche."""
        mock_provider = MockAuthProvider()
        jwks = mock_provider.get_jwks()
        
        assert "keys" in jwks
        assert len(jwks["keys"]) == 1
        assert jwks["keys"][0]["kid"] == "test-key-id"


# Fixture per il client di test
@pytest.fixture
def client():
    """Crea un test client FastAPI."""
    from fastapi.testclient import TestClient
    from src.main import app
    
    return TestClient(app)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
