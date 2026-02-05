# Table of Contents

* [dos\_utility.storage](#dos_utility.storage)
  * [get\_storage](#dos_utility.storage.get_storage)

<a id="dos_utility.storage"></a>

# dos\_utility.storage

<a id="dos_utility.storage.get_storage"></a>

#### get\_storage

```python
def get_storage() -> StorageInterface
```

Get the appropriate storage interface based on configuration.
It can also be used as a dependency in FastAPI via injection.

**Returns**:

- `StorageInterface` - The storage interface instance.

