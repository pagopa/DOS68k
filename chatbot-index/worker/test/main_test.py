import pytest

from worker.main import main


@pytest.mark.asyncio
async def test_main():
    await main()

    assert True