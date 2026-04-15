from typing import Self, List, Dict, Optional, BinaryIO
from fastapi import HTTPException, status

from dos_utility.storage import ObjectInfo


# ---------------------------------------------------------------------------
# Shared data fixtures
# ---------------------------------------------------------------------------

MOCK_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
MOCK_INDEX_ID = "test-index"
MOCK_EXISTING_INDEXES = ["index-1", "index-2"]


# ---------------------------------------------------------------------------
# Storage mocks (for service tests)
# ---------------------------------------------------------------------------

class MockStorage:
    """In-memory storage mock."""

    def __init__(self: Self, initial_objects: Optional[Dict[str, List[str]]] = None):
        self._objects: Dict[str, List[str]] = {}
        if initial_objects:
            for bucket, keys in initial_objects.items():
                self._objects[bucket] = list(keys)
        self.put_calls: List[dict] = []

    def is_healthy(self: Self) -> bool:
        return True

    def put_object(self: Self, bucket: str, name: str, data: BinaryIO, content_type: str) -> None:
        if bucket not in self._objects:
            self._objects[bucket] = []
        if name not in self._objects[bucket]:
            self._objects[bucket].append(name)
        self.put_calls.append({"bucket": bucket, "name": name, "content_type": content_type})

    def list_objects(self: Self, bucket: str) -> List[ObjectInfo]:
        return [ObjectInfo(key=k) for k in self._objects.get(bucket, [])]

    def delete_object(self: Self, bucket: str, name: str) -> None:
        keys = self._objects.get(bucket, [])
        if name in keys:
            keys.remove(name)


# ---------------------------------------------------------------------------
# VectorDB mocks (for service tests)
# ---------------------------------------------------------------------------

class MockVectorDBWithIndexes:
    """VectorDB mock with pre-existing indexes."""

    def __init__(self: Self, indexes: Optional[List[str]] = None):
        self._indexes: List[str] = list(indexes) if indexes is not None else list(MOCK_EXISTING_INDEXES)
        self.deleted_ids: List[str] = []

    async def get_indexes(self: Self) -> List[str]:
        return list(self._indexes)

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        self.deleted_ids.extend(ids)


class MockVectorDBEmpty:
    """VectorDB mock with no indexes."""

    async def get_indexes(self: Self) -> List[str]:
        return []

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        pass


# ---------------------------------------------------------------------------
# Queue mocks (for service tests)
# ---------------------------------------------------------------------------

class MockQueueClient:
    """Async queue mock."""

    def __init__(self: Self):
        self.enqueued: List[bytes] = []

    async def enqueue(self: Self, msg: bytes) -> str:
        self.enqueued.append(msg)
        return "mock-msg-id"


# ---------------------------------------------------------------------------
# Service mocks (for controller tests)
# ---------------------------------------------------------------------------

def get_document_service_upload_202_mock():
    class DocumentServiceMock:
        async def upload_document(self, index_id: str, file, user: str):
            return {
                "index_id": index_id,
                "document_name": file.filename,
                "message": f"Document '{file.filename}' uploaded successfully",
            }

    return DocumentServiceMock()


def get_document_service_upload_404_mock():
    class DocumentServiceMock:
        async def upload_document(self, index_id: str, file, user: str):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index '{index_id}' not found",
            )

    return DocumentServiceMock()


def get_document_service_upload_415_mock():
    class DocumentServiceMock:
        async def upload_document(self, index_id: str, file, user: str):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type '.docx'. Allowed types: .md, .pdf, .txt",
            )

    return DocumentServiceMock()


def get_document_service_list_200_mock():
    class DocumentServiceMock:
        async def list_documents(self, index_id: str):
            return [
                {"document_name": "file1.pdf"},
                {"document_name": "file2.md"},
            ]

    return DocumentServiceMock()


def get_document_service_list_empty_mock():
    class DocumentServiceMock:
        async def list_documents(self, index_id: str):
            return []

    return DocumentServiceMock()


def get_document_service_list_404_mock():
    class DocumentServiceMock:
        async def list_documents(self, index_id: str):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index '{index_id}' not found",
            )

    return DocumentServiceMock()


def get_document_service_delete_200_mock():
    class DocumentServiceMock:
        async def delete_document(self, index_id: str, document_name: str):
            return

    return DocumentServiceMock()


def get_document_service_delete_404_mock():
    class DocumentServiceMock:
        async def delete_document(self, index_id: str, document_name: str):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{document_name}' not found in index '{index_id}'",
            )

    return DocumentServiceMock()
