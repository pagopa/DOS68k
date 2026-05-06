import json
import pytest

from src.worker import task
from src.worker.loaders import Document
from src.worker.parsers import ChunkData
from dos_utility.vector_db import ObjectData, SearchResult

from test.worker.mocks import (
    GlobalSettingsMock,
    TaskSettingsMock,
    StorageSettingsMock,
    LoggerMock,
    VectorDBMock,
    make_vector_db_ctx_mock,
)

TASK_BODY = json.dumps(
    {
        "indexId": "idx1",
        "userId": "user1",
        "objectKey": "doc.pdf",
        "documentType": "application/pdf",
    }
).encode()

_MOCK_DOCUMENT = Document(filename="doc.pdf", content=["page 1"])
_MOCK_CHUNKS = [ChunkData(filename="doc.pdf", chunk_id=0, content="chunk 1")]
_MOCK_OBJECTS = [
    ObjectData(filename="doc.pdf", chunk_id=0, content="chunk 1", vector=[0.1, 0.2])
]


def _make_loader_mock():
    class _LoaderMock:
        def read(self, message):
            return _MOCK_DOCUMENT

    return _LoaderMock()


def _make_parser_mock():
    class _ParserMock:
        def transform(self, document):
            return _MOCK_CHUNKS

    return _ParserMock()


def _make_embedder_mock():
    class _EmbedderMock:
        def transform(self, chunks):
            return _MOCK_OBJECTS

    return _EmbedderMock()


def _patch_dependencies(monkeypatch, vdb_mock: VectorDBMock):
    monkeypatch.setattr(task, "get_global_settings", lambda: GlobalSettingsMock())
    monkeypatch.setattr(task, "get_task_settings", lambda: TaskSettingsMock())
    monkeypatch.setattr(task, "get_storage_settings", lambda: StorageSettingsMock())
    monkeypatch.setattr(task, "get_logger", lambda name, level: LoggerMock())
    monkeypatch.setattr(
        task, "get_document_loader", lambda bucket_name: _make_loader_mock()
    )
    monkeypatch.setattr(
        task, "get_parser", lambda chunk_size, chunk_overlap: _make_parser_mock()
    )
    monkeypatch.setattr(task, "get_embedder", lambda **kwargs: _make_embedder_mock())
    monkeypatch.setattr(task, "get_vector_db_ctx", make_vector_db_ctx_mock(vdb_mock))


async def test_process_task_index_not_exists(monkeypatch):
    vdb_mock = VectorDBMock(indexes=[])
    _patch_dependencies(monkeypatch, vdb_mock)

    await task.process_task(body=TASK_BODY)

    assert len(vdb_mock.create_index_calls) == 1
    assert vdb_mock.create_index_calls[0]["index_name"] == "idx1"
    assert vdb_mock.create_index_calls[0]["vector_dim"] == 768
    assert len(vdb_mock.put_calls) == 1
    assert vdb_mock.put_calls[0]["index_name"] == "idx1"
    assert len(vdb_mock.delete_calls) == 0


async def test_process_task_index_exists(monkeypatch):
    existing_results = [
        SearchResult(
            id="old_id_1", filename="doc.pdf", chunk_id=0, content="old", score=None
        ),
    ]
    vdb_mock = VectorDBMock(indexes=["idx1"], filter_results=existing_results)
    _patch_dependencies(monkeypatch, vdb_mock)

    await task.process_task(body=TASK_BODY)

    assert len(vdb_mock.create_index_calls) == 0
    assert len(vdb_mock.put_calls) == 1
    assert len(vdb_mock.delete_calls) == 1
    assert vdb_mock.delete_calls[0]["ids"] == ["old_id_1"]


async def test_process_task_delete_called_on_put_failure(monkeypatch):
    class _VectorDBPutFailsMock(VectorDBMock):
        async def put_objects(self, index_name: str, data: list) -> None:
            raise RuntimeError("put failed")

    vdb_mock = _VectorDBPutFailsMock(indexes=[])
    _patch_dependencies(monkeypatch, vdb_mock)

    with pytest.raises(RuntimeError, match="put failed"):
        await task.process_task(body=TASK_BODY)

    assert len(vdb_mock.delete_calls) == 0
