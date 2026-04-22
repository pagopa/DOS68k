import json
import pytest

from fastapi import HTTPException
from unittest.mock import MagicMock, AsyncMock

from src.modules.document.service import DocumentService, BUCKET_NAME
from src.modules.document.dto import UploadDocumentResponse, DocumentInfo

from test.modules.document.mocks import (
    MOCK_USER_ID,
    MOCK_EXISTING_INDEXES,
    MockStorage,
    MockVectorDBWithIndexes,
    MockVectorDBEmpty,
    MockQueueClient,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_upload_file(
    filename: str,
    content: bytes = b"test content",
    content_type: str = "application/pdf",
):
    mock_file = MagicMock()
    mock_file.filename = filename
    mock_file.content_type = content_type
    mock_file.read = AsyncMock(return_value=content)
    return mock_file


def make_service(vdb=None, storage=None, queue=None) -> DocumentService:
    return DocumentService(
        vdb=vdb or MockVectorDBWithIndexes(),
        storage=storage or MockStorage(),
        queue=queue or MockQueueClient(),
    )


# ---------------------------------------------------------------------------
# _validate_file_extension
# ---------------------------------------------------------------------------


def test_validate_file_extension_pdf():
    DocumentService._validate_file_extension("document.pdf")


def test_validate_file_extension_md():
    DocumentService._validate_file_extension("notes.md")


def test_validate_file_extension_txt():
    DocumentService._validate_file_extension("readme.txt")


def test_validate_file_extension_uppercase():
    DocumentService._validate_file_extension("DOCUMENT.PDF")


def test_validate_file_extension_invalid_raises_415():
    with pytest.raises(HTTPException) as exc_info:
        DocumentService._validate_file_extension("file.docx")
    assert exc_info.value.status_code == 415
    assert ".docx" in exc_info.value.detail


def test_validate_file_extension_no_extension_raises_415():
    with pytest.raises(HTTPException) as exc_info:
        DocumentService._validate_file_extension("filename")
    assert exc_info.value.status_code == 415


# ---------------------------------------------------------------------------
# upload_document
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upload_document_success():
    index_id = MOCK_EXISTING_INDEXES[0]
    queue = MockQueueClient()
    storage = MockStorage()
    service = make_service(queue=queue, storage=storage)

    file = make_upload_file("doc.pdf")
    result: UploadDocumentResponse = await service.upload_document(
        index_id=index_id, file=file, user=MOCK_USER_ID
    )

    assert result.index_id == index_id
    assert result.document_name == "doc.pdf"
    assert "uploaded successfully" in result.message

    assert len(queue.enqueued) == 1
    msg = json.loads(queue.enqueued[0])
    assert msg["indexId"] == index_id
    assert msg["userId"] == MOCK_USER_ID
    assert msg["objectKey"] == f"{index_id}/doc.pdf"
    assert msg["documentType"] == "application/pdf"

    stored = storage.list_objects(bucket=BUCKET_NAME)
    assert any(o.key == f"{index_id}/doc.pdf" for o in stored)


@pytest.mark.asyncio
async def test_upload_document_txt_and_md_accepted():
    index_id = MOCK_EXISTING_INDEXES[0]
    service = make_service()

    for filename in ("readme.txt", "notes.md"):
        file = make_upload_file(filename)
        result = await service.upload_document(
            index_id=index_id, file=file, user=MOCK_USER_ID
        )
        assert result.document_name == filename


@pytest.mark.asyncio
async def test_upload_document_invalid_extension_raises_415():
    service = make_service()
    file = make_upload_file("spreadsheet.xlsx")

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_document(
            index_id=MOCK_EXISTING_INDEXES[0], file=file, user=MOCK_USER_ID
        )
    assert exc_info.value.status_code == 415


@pytest.mark.asyncio
async def test_upload_document_index_not_found_raises_404():
    service = make_service(vdb=MockVectorDBEmpty())
    file = make_upload_file("doc.pdf")

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_document(
            index_id="nonexistent", file=file, user=MOCK_USER_ID
        )
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_document_none_content_type_falls_back():
    index_id = MOCK_EXISTING_INDEXES[0]
    queue = MockQueueClient()
    service = make_service(queue=queue)

    file = make_upload_file("doc.pdf", content_type=None)
    await service.upload_document(index_id=index_id, file=file, user=MOCK_USER_ID)

    msg = json.loads(queue.enqueued[0])
    assert msg["documentType"] is None

    assert len(queue.enqueued) == 1


# ---------------------------------------------------------------------------
# list_documents
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_documents_returns_only_matching_prefix():
    index_id = MOCK_EXISTING_INDEXES[0]
    storage = MockStorage(
        initial_objects={
            BUCKET_NAME: [
                f"{index_id}/doc1.pdf",
                f"{index_id}/doc2.md",
                "other-index/doc3.txt",
            ]
        }
    )
    service = make_service(storage=storage)

    result = await service.list_documents(index_id=index_id)

    assert len(result) == 2
    names = [d.document_name for d in result]
    assert "doc1.pdf" in names
    assert "doc2.md" in names


@pytest.mark.asyncio
async def test_list_documents_empty_bucket():
    service = make_service()
    result = await service.list_documents(index_id=MOCK_EXISTING_INDEXES[0])
    assert result == []


@pytest.mark.asyncio
async def test_list_documents_index_not_found_raises_404():
    service = make_service(vdb=MockVectorDBEmpty())

    with pytest.raises(HTTPException) as exc_info:
        await service.list_documents(index_id="nonexistent")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail


# ---------------------------------------------------------------------------
# delete_document
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_document_success():
    index_id = MOCK_EXISTING_INDEXES[0]
    object_key = f"{index_id}/doc.pdf"
    storage = MockStorage(initial_objects={BUCKET_NAME: [object_key]})
    vdb = MockVectorDBWithIndexes()
    service = make_service(vdb=vdb, storage=storage)

    await service.delete_document(index_id=index_id, document_name="doc.pdf")

    remaining = storage.list_objects(bucket=BUCKET_NAME)
    assert not any(o.key == object_key for o in remaining)
    assert object_key in vdb.deleted_ids


@pytest.mark.asyncio
async def test_delete_document_index_not_found_raises_404():
    service = make_service(vdb=MockVectorDBEmpty())

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_document(index_id="nonexistent", document_name="doc.pdf")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_document_file_not_found_raises_404():
    index_id = MOCK_EXISTING_INDEXES[0]
    service = make_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_document(index_id=index_id, document_name="missing.pdf")
    assert exc_info.value.status_code == 404
    assert "missing.pdf" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_document_does_not_delete_other_files():
    index_id = MOCK_EXISTING_INDEXES[0]
    other_key = f"{index_id}/other.pdf"
    target_key = f"{index_id}/target.pdf"
    storage = MockStorage(initial_objects={BUCKET_NAME: [target_key, other_key]})
    service = make_service(storage=storage)

    await service.delete_document(index_id=index_id, document_name="target.pdf")

    remaining = storage.list_objects(bucket=BUCKET_NAME)
    keys = [o.key for o in remaining]
    assert other_key in keys
    assert target_key not in keys
