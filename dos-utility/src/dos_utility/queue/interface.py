from abc import ABC, abstractmethod
from typing import Self, Tuple, Optional


class QueueInterface(ABC):
    @abstractmethod
    async def __aenter__(self: Self) -> Self:
        """Enter the asynchronous context manager.

        Returns:
            Self: The instance of the queue client.

        Examples:
            >>> queue = MyQueueImplementation()
            >>> async with queue as qc:
            >>>     # Use qc to interact with the queue
        """
        ...

    @abstractmethod
    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        """Exit the asynchronous context manager.

        Examples:
            >>> queue = MyQueueImplementation()
            >>> async with queue as qc:
            >>>     # Use qc to interact with the queue
        """
        ...

    @abstractmethod
    async def is_healthy(self: Self) -> bool:
        """Check if the queue service is healthy/reachable.
        If the implementation could raise an exception when not healthy, it should be caught and False returned.

        Returns:
            bool: True if healthy, False otherwise.
        """
        ...

    @abstractmethod
    async def enqueue(self: Self, msg: bytes) -> str:
        """Enqueue a message to the queue.

        Args:
            msg (bytes): The message to enqueue.

        Returns:
            str: message id.

        Examples:
            >>> msg_id: str = await queue_client.enqueue(msg=b"Hello World!")
            >>> msg_id: str = await queue_client.enqueue(msg=json.dumps({"message": "Hello World!"}).encode("utf-8"))
        """
        ...

    @abstractmethod
    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        """Dequeue a message from the queue.

        Returns:
            Tuple[Optional[bytes], Optional[str]]: A tuple containing the dequeued message (bytes) and its acknowledgment token (str).
            If the queue is empty, both values will be None.

        Examples:
            >>> msg, ack_token = await queue_client.dequeue()
            >>> if msg is not None:
            >>>     converted_data = json.loads(msg.decode("utf-8"))
            >>>     # Process the message...
            >>>     await queue_client.acknowledge(ack_token=ack_token)
        """
        ...

    @abstractmethod
    async def acknowledge(self: Self, ack_token: str) -> None:
        """Acknowledge the processing of a message using its acknowledgment token.
        The acknowledgment token is obtained when dequeuing a message.

        Args:
            ack_token (str): The acknowledgment token of the message to acknowledge.

        Examples: look at `dequeue` method.
        """
        ...
