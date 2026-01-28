import logging

from uuid import uuid4
from typing import Self, Tuple, List, Optional
from redis import ResponseError
from redis.asyncio import Redis

from ..interface import QueueInterface
from .connection import get_queue_pool
from .env import RedisQueueSettings, get_redis_queue_settings


class RedisQueue(QueueInterface):
    def __init__(self: Self) -> None:
        self._settings: RedisQueueSettings = get_redis_queue_settings() # Load redis env variables

    async def __aenter__(self: Self) -> Self:
        self._redis_client: Redis = Redis(connection_pool=get_queue_pool()) # Create redis client

        # Create group if it doesn't exist (id="0" = read old; "$" = only new)
        try:
            await self._redis_client.xgroup_create(
                name=self._settings.REDIS_STREAM,
                groupname=self._settings.REDIS_GROUP,
                id="0",
                mkstream=True,
            )
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                logging.info("Redis group already exists, ignoring error")
            else:
                raise # Reraise other exceptions

        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        await self._redis_client.aclose() # Close redis client connection

    async def is_healthy(self: Self) -> bool:
        try:
            # Check Redis connection health
            pong: bool = await self._redis_client.ping()

            return pong
        except Exception as e:
            logging.error(f"Redis health check failed: {e}")

            return False
    
    async def enqueue(self: Self, msg: bytes) -> str:
        msg_id: str = await self._redis_client.xadd(name=self._settings.REDIS_STREAM, fields={b"body": msg}) # Add message to Redis stream

        return msg_id

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        response: List = await self._redis_client.xreadgroup(
            groupname=self._settings.REDIS_GROUP,
            consumername=uuid4().hex,
            streams={self._settings.REDIS_STREAM: ">"}, # read new messages
            count=1,
            block=1,
            noack=True,
        )

        if len(response) > 0:
            for _, messages in response:
                for message_id, message_data in messages:
                    return message_data[b"body"], message_id

        return None, None

    async def acknowledge(self: Self, ack_token: str) -> None:
        # Acknowledge message processing
        _ = await self._redis_client.xack(self._settings.REDIS_STREAM, self._settings.REDIS_GROUP, ack_token)


def get_redis_queue() -> RedisQueue:
    return RedisQueue()
