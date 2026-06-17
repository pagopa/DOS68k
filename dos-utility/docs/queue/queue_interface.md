# Table of Contents

* [dos\_utility.queue.interface](#dos_utility.queue.interface)
  * [QueueInterface](#dos_utility.queue.interface.QueueInterface)
    * [\_\_aenter\_\_](#dos_utility.queue.interface.QueueInterface.__aenter__)
    * [\_\_aexit\_\_](#dos_utility.queue.interface.QueueInterface.__aexit__)
    * [is\_healthy](#dos_utility.queue.interface.QueueInterface.is_healthy)
    * [enqueue](#dos_utility.queue.interface.QueueInterface.enqueue)
    * [dequeue](#dos_utility.queue.interface.QueueInterface.dequeue)
    * [acknowledge](#dos_utility.queue.interface.QueueInterface.acknowledge)

<a id="dos_utility.queue.interface"></a>

# dos\_utility.queue.interface

<a id="dos_utility.queue.interface.QueueInterface"></a>

## QueueInterface Objects

```python
class QueueInterface(ABC)
```

<a id="dos_utility.queue.interface.QueueInterface.__aenter__"></a>

#### \_\_aenter\_\_

```python
@abstractmethod
async def __aenter__() -> Self
```

Enter the asynchronous context manager.

**Returns**:

- `Self` - The instance of the queue client.
  

**Examples**:

  >>> queue = MyQueueImplementation()
  >>> async with queue as qc:
  >>>     # Use qc to interact with the queue

<a id="dos_utility.queue.interface.QueueInterface.__aexit__"></a>

#### \_\_aexit\_\_

```python
@abstractmethod
async def __aexit__(exc_type, exc_val, exc_tb) -> None
```

Exit the asynchronous context manager.

**Examples**:

  >>> queue = MyQueueImplementation()
  >>> async with queue as qc:
  >>>     # Use qc to interact with the queue

<a id="dos_utility.queue.interface.QueueInterface.is_healthy"></a>

#### is\_healthy

```python
@abstractmethod
async def is_healthy() -> bool
```

Check if the queue service is healthy/reachable.
If the implementation could raise an exception when not healthy, it should be caught and False returned.

**Returns**:

- `bool` - True if healthy, False otherwise.

<a id="dos_utility.queue.interface.QueueInterface.enqueue"></a>

#### enqueue

```python
@abstractmethod
async def enqueue(msg: bytes) -> str
```

Enqueue a message to the queue.

**Arguments**:

- `msg` _bytes_ - The message to enqueue.
  

**Returns**:

- `str` - message id.
  

**Examples**:

  >>> msg_id: str = await queue_client.enqueue(msg=b"Hello World!")
  >>> msg_id: str = await queue_client.enqueue(msg=json.dumps({"message": "Hello World!"}).encode("utf-8"))

<a id="dos_utility.queue.interface.QueueInterface.dequeue"></a>

#### dequeue

```python
@abstractmethod
async def dequeue() -> Tuple[Optional[bytes], Optional[str]]
```

Dequeue a message from the queue.

**Returns**:

  Tuple[Optional[bytes], Optional[str]]: A tuple containing the dequeued message (bytes) and its acknowledgment token (str).
  If the queue is empty, both values will be None.
  

**Examples**:

  >>> msg, ack_token = await queue_client.dequeue()
  >>> if msg is not None:
  >>>     converted_data = json.loads(msg.decode("utf-8"))
  >>>     # Process the message...
  >>>     await queue_client.acknowledge(ack_token=ack_token)

<a id="dos_utility.queue.interface.QueueInterface.acknowledge"></a>

#### acknowledge

```python
@abstractmethod
async def acknowledge(ack_token: str) -> None
```

Acknowledge the processing of a message using its acknowledgment token.
The acknowledgment token is obtained when dequeuing a message.

**Arguments**:

- `ack_token` _str_ - The acknowledgment token of the message to acknowledge.
  
- `Examples` - look at `dequeue` method.

