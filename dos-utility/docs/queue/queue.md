# Table of Contents

* [dos\_utility.queue](#dos_utility.queue)
  * [get\_queue\_client\_ctx](#dos_utility.queue.get_queue_client_ctx)
  * [get\_queue\_client](#dos_utility.queue.get_queue_client)

<a id="dos_utility.queue"></a>

# dos\_utility.queue

<a id="dos_utility.queue.get_queue_client_ctx"></a>

#### get\_queue\_client\_ctx

```python
@asynccontextmanager
async def get_queue_client_ctx() -> AsyncGenerator[QueueInterface, None]
```

Asynchronous context manager to get the appropriate queue client based on configuration.

**Yields**:

  AsyncGenerator[QueueInterface, None]: An instance of the appropriate queue client.
  

**Examples**:

  >>> async with get_queue_client_ctx() as queue_client:
  >>>     msg_id = await queue_client.enqueue(msg=b"Hello World!")

<a id="dos_utility.queue.get_queue_client"></a>

#### get\_queue\_client

```python
async def get_queue_client() -> AsyncGenerator[QueueInterface, None]
```

FastAPI dependency to get the appropriate queue client based on configuration.

**Yields**:

  AsyncGenerator[QueueInterface, None]: An instance of the appropriate queue client.
  

**Examples**:

  >>> @app.post("/enqueue")
  >>> async def enqueue_message(queue_client: Annotated[QueueInterface, Depends(get_queue_client)]):
  >>>     msg_id = await queue_client.enqueue(msg=b"Hello World!")

