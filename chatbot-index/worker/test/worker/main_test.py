import traceback as traceback_module
import pytest

from src.worker import main

from test.worker.mocks import (
    GlobalSettingsMock,
    LoggerMock,
    QueueClientMock,
    make_queue_client_ctx_mock,
)

_TASK_BODY = b'{"indexId": "idx1", "userId": "user1", "objectKey": "doc.pdf", "documentType": "application/pdf"}'


def _patch_dependencies(monkeypatch, queue_client: QueueClientMock):
    monkeypatch.setattr(main, "get_global_settings", lambda: GlobalSettingsMock())
    monkeypatch.setattr(main, "get_logger", lambda name, level: LoggerMock())
    monkeypatch.setattr(
        main, "get_queue_client_ctx", make_queue_client_ctx_mock(queue_client)
    )


async def test_main_processes_task_and_acknowledges(monkeypatch):
    queue_client = QueueClientMock(messages=[_TASK_BODY], ack_tokens=["ack_1"])
    _patch_dependencies(monkeypatch, queue_client)

    process_task_calls = []

    async def _mock_process_task(body):
        process_task_calls.append(body)

    monkeypatch.setattr(main, "process_task", _mock_process_task)

    with pytest.raises(SystemExit):
        await main.main()

    assert process_task_calls == [_TASK_BODY]
    assert queue_client.acknowledged == ["ack_1"]


async def test_main_skips_acknowledge_when_ack_token_is_none(monkeypatch):
    queue_client = QueueClientMock(messages=[_TASK_BODY], ack_tokens=[None])
    _patch_dependencies(monkeypatch, queue_client)

    async def _mock_process_task(body):
        pass

    monkeypatch.setattr(main, "process_task", _mock_process_task)

    with pytest.raises(SystemExit):
        await main.main()

    assert queue_client.acknowledged == []


async def test_main_skips_processing_when_no_message(monkeypatch):
    queue_client = QueueClientMock(messages=[None], ack_tokens=[None])
    _patch_dependencies(monkeypatch, queue_client)

    process_task_calls = []

    async def _mock_process_task(body):
        process_task_calls.append(body)

    monkeypatch.setattr(main, "process_task", _mock_process_task)

    with pytest.raises(SystemExit):
        await main.main()

    assert process_task_calls == []


async def test_main_catches_process_task_exception(monkeypatch):
    queue_client = QueueClientMock(
        messages=[_TASK_BODY, _TASK_BODY],
        ack_tokens=["ack_1", "ack_2"],
    )
    _patch_dependencies(monkeypatch, queue_client)

    call_count = [0]

    async def _mock_process_task(body):
        call_count[0] += 1
        raise Exception("processing error")

    monkeypatch.setattr(main, "process_task", _mock_process_task)

    with pytest.raises(SystemExit):
        await main.main()

    assert call_count[0] == 2
    assert queue_client.acknowledged == []
