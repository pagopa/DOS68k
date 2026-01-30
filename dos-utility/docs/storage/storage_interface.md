# Table of Contents

* [dos\_utility.storage.interface](#dos_utility.storage.interface)
  * [ObjectInfo](#dos_utility.storage.interface.ObjectInfo)
  * [StorageInterface](#dos_utility.storage.interface.StorageInterface)
    * [is\_healthy](#dos_utility.storage.interface.StorageInterface.is_healthy)
    * [get\_object](#dos_utility.storage.interface.StorageInterface.get_object)
    * [put\_object](#dos_utility.storage.interface.StorageInterface.put_object)
    * [delete\_object](#dos_utility.storage.interface.StorageInterface.delete_object)
    * [list\_objects](#dos_utility.storage.interface.StorageInterface.list_objects)

<a id="dos_utility.storage.interface"></a>

# dos\_utility.storage.interface

<a id="dos_utility.storage.interface.ObjectInfo"></a>

## ObjectInfo Objects

```python
@dataclass
class ObjectInfo()
```

Information about an object stored in the storage service.

**Attributes**:

- `key` _str_ - The key (name) of the object. It can be use to retrieve the object with the `get_object` method.

<a id="dos_utility.storage.interface.StorageInterface"></a>

## StorageInterface Objects

```python
class StorageInterface(ABC)
```

<a id="dos_utility.storage.interface.StorageInterface.is_healthy"></a>

#### is\_healthy

```python
@abstractmethod
def is_healthy() -> bool
```

Check if the storage service is healthy and reachable.
If any exception occurs during the check, it should be interpreted as unhealthy and return False.

**Returns**:

- `bool` - True if the storage service is healthy, False otherwise.

<a id="dos_utility.storage.interface.StorageInterface.get_object"></a>

#### get\_object

```python
@abstractmethod
def get_object(bucket: str, name: str) -> BinaryIO
```

Retrieve an object from the storage.

**Arguments**:

- `bucket` _str_ - The name of the bucket.
- `name` _str_ - The name of the object.
  

**Returns**:

- `BinaryIO` - The binary data of the object.

<a id="dos_utility.storage.interface.StorageInterface.put_object"></a>

#### put\_object

```python
@abstractmethod
def put_object(bucket: str, name: str, data: BinaryIO,
               content_type: str) -> None
```

Store an object in the storage.

**Arguments**:

- `bucket` _str_ - The name of the bucket.
- `name` _str_ - The name of the object.
- `data` _BinaryIO_ - The binary data of the object.
- `content_type` _str_ - The content type of the object.

<a id="dos_utility.storage.interface.StorageInterface.delete_object"></a>

#### delete\_object

```python
@abstractmethod
def delete_object(bucket: str, name: str) -> None
```

Delete an object from the storage.

**Arguments**:

- `bucket` _str_ - The name of the bucket.
- `name` _str_ - The name of the object.

<a id="dos_utility.storage.interface.StorageInterface.list_objects"></a>

#### list\_objects

```python
@abstractmethod
def list_objects(bucket: str) -> List[ObjectInfo]
```

List all objects in a bucket.

**Arguments**:

- `bucket` _str_ - The name of the bucket.
  

**Returns**:

- `List[ObjectInfo]` - A list of ObjectInfo representing the objects in the bucket.

