# Authentication Providers

## Overview

The auth service uses pluggable JWT authentication providers via the Strategy Pattern. Provider implementations are in the `dos-utility` package, while this service exposes REST endpoints.

## Architecture

**Provider implementations** (`dos-utility` package):
```
dos-utility/src/dos_utility/auth/
├── interface.py          # AuthInterface (abstract)
├── __init__.py           # get_auth_provider() factory
├── aws/
│   └── implementation.py # AWS Cognito provider
└── local/
    └── implementation.py # Local mock provider
```

**Auth service** (this package):
```
auth/src/
├── routers/
│   ├── health.py         # Health check endpoint
│   └── jwt_check.py      # JWT verification endpoint
└── main.py               # FastAPI application
```

## Configuration

### AWS Cognito

```env
AUTH_PROVIDER=aws
AWS_REGION=us-east-1
AWS_COGNITO_REGION=us-east-1
AUTH_COGNITO_USERPOOL_ID=us-east-1_XXXXXXXXX

# Optional: for LocalStack
AWS_ENDPOINT_URL=http://localstack:4566
```

### Local (Development Only)

```env
AUTH_PROVIDER=local
```

⚠️ **WARNING**: The `local` provider bypasses JWT verification entirely and always returns mock claims. **Use only for local development.**

- ✅ **Use for**: frontend development, local testing, debugging
- ❌ **Never use in**: staging, production, security testing

**Local provider behavior**:
- `Authorization` header is **optional**
- Any token (even malformed) is accepted
- Always returns the same mock claims

Example request:
```bash
# Without header (local mode only)
curl http://localhost:3000/protected/jwt-check

# With header (all modes)
curl -H "Authorization: Bearer <token>" \
     http://localhost:3000/protected/jwt-check
```

## Usage

### In Routes

```python
from fastapi import APIRouter, Header, HTTPException, status
from dos_utility.auth import get_auth_provider

router = APIRouter(prefix="/protected")

@router.get("/jwt-check")
def jwt_check(Authorization: str = Header(...)):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Bearer token")
    
    token = Authorization.split(" ", 1)[1]
    provider = get_auth_provider()
    payload = provider.verify_jwt(token)
    
    return {"status": "ok", "payload": payload}
```

### Direct Usage

```python
from dos_utility.auth import get_auth_provider

provider = get_auth_provider()

# Verify JWT
claims = provider.verify_jwt(token)

# Get JWKS
jwks = provider.get_jwks()
```

## Adding New Providers

To add a new provider (e.g., Auth0):

1. **Implement in `dos-utility` package**:
```python
# dos-utility/src/dos_utility/auth/auth0/implementation.py
from dos_utility.auth.interface import AuthInterface

class Auth0Provider(AuthInterface):
    def get_jwks(self):
        # Fetch from Auth0
        ...
    
    def verify_jwt(self, token: str):
        # Verify token
        ...
```

2. **Register in factory**:
```python
# dos-utility/src/dos_utility/auth/__init__.py
from .auth0 import get_auth0_provider

def get_auth_provider() -> AuthInterface:
    if auth_settings.AUTH_PROVIDER is AuthProvider.AUTH0:
        return get_auth0_provider()
    # ...
```

3. **Add configuration**:
```env
AUTH_PROVIDER=auth0
AUTH0_DOMAIN=tenant.auth0.com
AUTH0_AUDIENCE=api-identifier
```

## Testing

Mock the provider in tests:

```python
from dos_utility.auth import AuthInterface

class MockAuthProvider(AuthInterface):
    def get_jwks(self):
        return {"keys": [{"kid": "test", "kty": "RSA"}]}
    
    def verify_jwt(self, token: str):
        if token == "valid":
            return {"sub": "user-123"}
        raise HTTPException(401, "Invalid token")
```

## API Endpoints

### GET /protected/jwt-check

Verifies a JWT token.

**Request**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200):
```json
{
  "status": "ok",
  "payload": {
    "sub": "user-id",
    "exp": 1234567890
  }
}
```

**Errors**:
- `401`: Invalid/expired token
- `422`: Missing Authorization header
- `500`: Provider error
