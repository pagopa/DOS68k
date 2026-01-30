import asyncio
import boto3
import base64
import logging

from uuid import uuid4
from typing import Self, Tuple, Optional

from ..interface import QueueInterface
from .env import SQSQueueSettings, get_sqs_queue_settings


class SQSQueue(QueueInterface):
    def __init__(self: Self) -> None:
        self._settings: SQSQueueSettings = get_sqs_queue_settings() # Load sqs env variables

    async def __aenter__(self: Self) -> Self:
        # Since boto3 is blocking, we run it in a separate thread to respect asyncio interface
        loop = asyncio.get_event_loop() # Get current event loop
        # Initialize SQS client
        self._client = await loop.run_in_executor(
            None,
            lambda: boto3.client(
                "sqs",
                region_name=self._settings.SQS_REGION,
                endpoint_url=f"{self._settings.SQS_ENDPOINT_URL}:{self._settings.SQS_PORT}",
                aws_access_key_id=self._settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self._settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            ),
        )

        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        # Boto3 clients do not require explicit closing
        pass

    async def is_healthy(self: Self) -> bool:
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self._client.get_queue_url(QueueName=self._settings.SQS_QUEUE_NAME), # Simple call to check if queue is accessible
            )

            return True
        except Exception as e:
            logging.error(f"SQS health check failed: {e}")

            return False

    async def enqueue(self: Self, msg: bytes) -> str:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.send_message(
                QueueUrl=self._settings.SQS_QUEUE_URL,
                MessageBody=base64.b64encode(msg).decode("utf-8"), # SQS only wants string messages, so we base64 encode the bytes
                MessageGroupId="default",
                MessageDeduplicationId=uuid4().hex,
            ),
        )

        return response["MessageId"]

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.receive_message(
                QueueUrl=self._settings.SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            ),
        )

        messages = response.get("Messages", [])

        if len(messages) > 0:
            message = messages[0]
            msg_body = base64.b64decode(message["Body"].encode("utf-8")) # Decode the base64 encoded message back to bytes, to respect the interface
            ack_token = message["ReceiptHandle"]

            return msg_body, ack_token

        return None, None

    async def acknowledge(self: Self, ack_token: str) -> None:
        loop = asyncio.get_event_loop()
        # Delete the message from the queue using the receipt handle. In SQS this is how we acknowledge message processing.
        await loop.run_in_executor(
            None,
            lambda: self._client.delete_message(
                QueueUrl=self._settings.SQS_QUEUE_URL,
                ReceiptHandle=ack_token,
            ),
        )

def get_sqs_queue() -> SQSQueue:
    return SQSQueue()
