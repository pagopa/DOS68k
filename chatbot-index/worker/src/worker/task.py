import asyncio
import json

from typing import Any


async def process_task(body: bytes) -> None:
    """Process a task with the given body.

    Args:
        body (bytes): The body of the task to be processed.
    """
    converted_data: Any = json.loads(body.decode("utf-8"))
