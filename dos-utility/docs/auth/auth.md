# Table of Contents

* [dos\_utility.auth](#dos_utility.auth)
  * [get\_auth](#dos_utility.auth.get_auth)

<a id="dos_utility.auth"></a>

# dos\_utility.auth

<a id="dos_utility.auth.get_auth"></a>

#### get\_auth

```python
def get_auth() -> AuthInterface
```

Get the configured authentication provider instance.

The provider is selected from the `AUTH_PROVIDER` environment variable, which must be a valid `AuthProvider` enum value. Pydantic validates this at startup, so no invalid value can reach the factory.

**Returns**:

  AuthInterface: An instance of the appropriate authentication provider.

**Configuration**:

```env
# Use AWS Cognito
AUTH_PROVIDER=aws

# Use local mock (development only)
AUTH_PROVIDER=local
```

**Examples**:

  >>> from dos_utility.auth import get_auth
  >>> provider = get_auth()
  >>> claims = provider.verify_jwt(token)

---

## Adding a New Provider

1. **Create the implementation** under `dos_utility/auth/<provider>/implementation.py`, extending `AuthInterface`.
   Follow the [implementation guidelines](./auth_interface.md#implementing-a-new-provider):
   - Guard `token == ""` → raise `EmptyTokenException`
   - Raise typed exceptions (`InvalidTokenKeyException`, `TokenExpiredException`, `InvalidTokenException`)
   - Never raise `HTTPException` from a provider

2. **Add the enum value** in `dos_utility/auth/env.py`:

```python
class AuthProvider(StrEnum):
    AWS = "aws"
    MY_PROVIDER = "myprovider"
    LOCAL = "local"
```

3. **Register in the factory** in `dos_utility/auth/__init__.py`:

```python
from .myprovider import get_my_provider

def get_auth() -> AuthInterface:
    if auth_settings.AUTH_PROVIDER is AuthProvider.AWS:
        return get_aws_auth_provider()
    elif auth_settings.AUTH_PROVIDER is AuthProvider.MY_PROVIDER:
        return get_my_provider()
    elif auth_settings.AUTH_PROVIDER is AuthProvider.LOCAL:
        return get_local_auth_provider()
```

4. **Document the required env vars** in the service's `README.AUTH_PROVIDERS.md`.
