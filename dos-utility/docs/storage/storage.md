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

**Examples**:

Standalone usage:

  >>> from dos_utility.storage import StorageInterface, get_storage
  >>> storage: StorageInterface = get_storage()
  >>> storage.put_object(bucket="my-bucket", name="file.pdf", data=file_data, content_type="application/pdf")
  >>> obj = storage.get_object(bucket="my-bucket", name="file.pdf")

As a FastAPI dependency:

  >>> from typing import Annotated
  >>> from fastapi import Depends
  >>> from dos_utility.storage import StorageInterface, get_storage
  >>>
  >>> @app.get("/files")
  >>> async def list_files(storage: Annotated[StorageInterface, Depends(get_storage)]):
  >>>     objects = storage.list_objects(bucket="my-bucket")
  >>>     return [obj.key for obj in objects]
