import pytest

from src.worker import main

from test.mocks import get_queue_client_ctx_mock, process_task_block_loop_mock, get_queue_client_loop_ctx_mock, StopAsyncIteration


@pytest.mark.asyncio
async def test_main_block_loop(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "get_queue_client_ctx", get_queue_client_ctx_mock)
    monkeypatch.setattr(main, "process_task", process_task_block_loop_mock)

    with pytest.raises(expected_exception=Exception, match="Simulated processing error"):
        await main.main()

@pytest.mark.asyncio
async def test_main_block_loop_at_second_iteration(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "get_queue_client_ctx", get_queue_client_loop_ctx_mock)

    with pytest.raises(expected_exception=StopAsyncIteration):
        await main.main()
