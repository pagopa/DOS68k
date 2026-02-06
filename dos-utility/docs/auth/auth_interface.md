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

  >>> auth_provider = get_auth_provider()
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

- `HTTPException` - If the token is invalid, expired, or verification fails
  

**Examples**:

  >>> auth_provider = get_auth_provider()
  >>> token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  >>> try:
  >>>     claims = auth_provider.verify_jwt(token)
  >>>     user_id = claims.get("sub")
  >>>     email = claims.get("email")
  >>>     print(f"User {user_id} authenticated successfully")
  >>> except HTTPException as e:
  >>>     print(f"Authentication failed: {e.detail}")
