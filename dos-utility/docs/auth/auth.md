# Table of Contents

* [dos\_utility.auth](#dos_utility.auth)
  * [get\_auth\_provider](#dos_utility.auth.get_auth_provider)

<a id="dos_utility.auth"></a>

# dos\_utility.auth

<a id="dos_utility.auth.get_auth_provider"></a>

#### get\_auth\_provider

```python
def get_auth_provider() -> AuthInterface
```

Get the configured authentication provider instance.

**Returns**:

  AuthInterface: An instance of the appropriate authentication provider.
  

**Raises**:

- `ValueError` - If the configured AUTH_PROVIDER is not supported
  

