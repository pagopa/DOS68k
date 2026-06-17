import pytest

from src.worker import main

from test.mocks import (
    get_queue_client_ctx_mock,
    get_queue_client_loop_ctx_mock,
    process_task_block_loop_mock,
    process_task_noop_mock,
    StopAsyncIteration,
)


@pytest.mark.asyncio
async def test_main_propagates_process_task_errors(monkeypatch: pytest.MonkeyPatch):
    """An error inside process_task must crash the worker.

    Regression risk: swallowing the exception would silently ack the message,
    losing it forever without surfacing the bug.
    """
    monkeypatch.setattr(main, "get_queue_client_ctx", get_queue_client_ctx_mock)
    monkeypatch.setattr(main, "process_task", process_task_block_loop_mock)

    with pytest.raises(
        expected_exception=Exception, match="Simulated processing error"
    ):
        await main.main()


@pytest.mark.asyncio
async def test_main_acknowledges_after_successful_processing(
    monkeypatch: pytest.MonkeyPatch,
):
    """A successful process_task must be followed by an ack.

    Regression risk: forgetting to ack would cause messages to be redelivered
    indefinitely, re-running expensive LLM evaluations on the same query.
    """
    monkeypatch.setattr(main, "get_queue_client_ctx", get_queue_client_loop_ctx_mock)
    monkeypatch.setattr(main, "process_task", process_task_noop_mock)

    # QueueClientLoopMock raises StopAsyncIteration from acknowledge() on the
    # first ack, proving the ack path was actually reached.
    with pytest.raises(expected_exception=StopAsyncIteration):
        await main.main()
