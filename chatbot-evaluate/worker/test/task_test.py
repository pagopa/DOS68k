import pytest

from src.worker import task

@pytest.mark.asyncio
async def test_process_task():
    body = b'{"task": "example", "data": 123}'
    await task.process_task(body=body)

    assert True
