# Table of Contents

* [dos\_utility.auth.interface](#dos_utility.auth.interface)
  * [AuthInterface](#dos_utility.auth.interface.AuthInterface)
    * [get\_jwks](#dos_utility.auth.interface.AuthInterface.get_jwks)
    * [verify\_jwt](#dos_utility.auth.interface.AuthInterface.verify_jwt)

<a id="dos_utility.auth.interface"></a>

# dos\_utility.auth.interface

<a id="dos_utility.auth.interface.AuthInterface"></a>

## AuthInterface Objects

```python
class AuthInterface(ABC)
```

Abstract base class for authentication providers.
All concrete implementations must extend this class and implement its abstract methods.

<a id="dos_utility.auth.interface.AuthInterface.get_jwks"></a>

#### get\_jwks

```python
@abstractmethod
def get_jwks() -> Dict[str, Any]
```

Retrieve the JSON Web Key Set (JWKS) from the authentication provider.

**Returns**:

- `Dict[str, Any]` - The JWKS containing the public keys


**Raises**:

- `HTTPException` - If the JWKS cannot be retrieved


**Examples**:

  >>> auth_provider = get_auth()
  >>> jwks = auth_provider.get_jwks()
  >>> print(jwks["keys"])

<a id="dos_utility.auth.interface.AuthInterface.verify_jwt"></a>

#### verify\_jwt

```python
@abstractmethod
def verify_jwt(token: str) -> Dict[str, Any]
```

Verify a JWT token and return its claims.

**Arguments**:

- `token` _str_ - The JWT token to verify


**Returns**:

- `Dict[str, Any]` - The verified token claims


**Raises**:

- `EmptyTokenException` - If `token` is an empty string
- `InvalidTokenKeyException` - If the token's key ID is not found in the JWKS or signature verification fails
- `TokenExpiredException` - If the token has expired
- `InvalidTokenException` - If the token is malformed or otherwise invalid


**Examples**:

  >>> from dos_utility.auth import get_auth, EmptyTokenException, TokenExpiredException, InvalidTokenException, InvalidTokenKeyException
  >>> auth_provider = get_auth()
  >>> token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  >>> try:
  >>>     claims = auth_provider.verify_jwt(token)
  >>>     user_id = claims.get("sub")
  >>>     email = claims.get("email")
  >>>     print(f"User {user_id} authenticated successfully")
  >>> except EmptyTokenException:
  >>>     print("Token is empty")
  >>> except TokenExpiredException:
  >>>     print("Token has expired")
  >>> except (InvalidTokenException, InvalidTokenKeyException) as e:
  >>>     print(f"Token is invalid: {e}")

---

## Implementing a New Provider

When implementing `AuthInterface`, follow these conventions so all providers behave consistently.

### 1. Guard against an empty token

Check for `token == ""` **before** any parsing or network call and raise `EmptyTokenException`:

```python
def verify_jwt(self, token: str) -> Dict[str, Any]:
    if token == "":
        raise EmptyTokenException

    # ... verification logic
```

### 2. Raise typed exceptions

Use the domain exceptions from `dos_utility.auth.exceptions` instead of `HTTPException`:

| Situation | Exception to raise |
|---|---|
| Token is an empty string | `EmptyTokenException` |
| Key ID (`kid`) not found in JWKS, or signature check fails | `InvalidTokenKeyException` |
| Token has expired | `TokenExpiredException` |
| Token is malformed or any other JWT parse error | `InvalidTokenException` |

The service layer is responsible for translating these into HTTP responses. Providers must not raise `HTTPException` directly.

### 3. Example skeleton

```python
from dos_utility.auth.interface import AuthInterface
from dos_utility.auth.exceptions import (
    EmptyTokenException,
    InvalidTokenKeyException,
    TokenExpiredException,
    InvalidTokenException,
)

class MyProvider(AuthInterface):
    def get_jwks(self) -> Dict[str, Any]:
        # fetch and return the JWKS
        ...

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        if token == "":
            raise EmptyTokenException

        try:
            # ... verify and decode the token
            claims = decode(token)
        except KeyIDNotFound:
            raise InvalidTokenKeyException
        except ExpiredError:
            raise TokenExpiredException
        except Exception:
            raise InvalidTokenException

        return claims
```
