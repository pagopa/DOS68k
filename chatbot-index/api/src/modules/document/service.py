import json

from io import BytesIO
from typing import Self, List, Annotated
from fastapi import Depends, HTTPException, UploadFile, status

from dos_utility.vector_db import VectorDBInterface, get_vector_db
from dos_utility.storage import StorageInterface, get_storage
from dos_utility.queue import QueueInterface, get_queue_client

from .dto import UploadDocumentResponse, DocumentInfo
from ..index.service import IndexService, get_index_service
from ...env import get_index_bucket_settings, IndexBucketSettings


ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


class DocumentService:
    def __init__(
        self: Self,
        vdb: VectorDBInterface,
        storage: StorageInterface,
        queue: QueueInterface,
        index_service: IndexService,
    ):
        self.vdb: VectorDBInterface = vdb
        self.storage: StorageInterface = storage
        self.queue: QueueInterface = queue
        self.index_bucket_settings: IndexBucketSettings = get_index_bucket_settings()
        self.index_service: IndexService = index_service

    @staticmethod
    def _validate_file_extension(filename: str) -> None:
        ext: str = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

    async def upload_document(
        self: Self, index_id: str, file: UploadFile, user: str
    ) -> UploadDocumentResponse:
        self._validate_file_extension(file.filename)
        await self.index_service.verify_index_exists(index_id=index_id)

        content: bytes = await file.read()
        object_key: str = f"{index_id}/{file.filename}"

        self.storage.put_object(
            bucket=self.index_bucket_settings.index_documents_bucket_name,
            name=object_key,
            data=BytesIO(content),
            content_type=file.content_type or "application/octet-stream",
        )
        msg: dict = {
            "indexId": index_id,
            "userId": user,
            "objectKey": object_key,
            "documentType": file.content_type,
        }
        await self.queue.enqueue(msg=json.dumps(msg).encode("utf-8"))

        return UploadDocumentResponse(
            index_id=index_id,
            document_name=file.filename,
            message=f"Document '{file.filename}' uploaded successfully",
        )

    async def list_documents(self: Self, index_id: str) -> List[DocumentInfo]:
        await self.index_service.verify_index_exists(index_id=index_id)

        objects = self.storage.list_objects(bucket=self.index_bucket_settings.index_documents_bucket_name)
        prefix: str = f"{index_id}/"

        return [
            DocumentInfo(document_name=obj.key.removeprefix(prefix))
            for obj in objects
            if obj.key.startswith(prefix)
        ]

    async def delete_document(self: Self, index_id: str, document_name: str) -> None:
        await self.index_service.verify_index_exists(index_id=index_id)

        object_key: str = f"{index_id}/{document_name}"
        objects = self.storage.list_objects(bucket=self.index_bucket_settings.index_documents_bucket_name)
        if not any(obj.key == object_key for obj in objects):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{document_name}' not found in index '{index_id}'",
            )

        self.storage.delete_object(bucket=self.index_bucket_settings.index_documents_bucket_name, name=object_key)
        await self.vdb.delete_objects(index_name=index_id, ids=[object_key])


def get_document_service(
    vdb: Annotated[VectorDBInterface, Depends(dependency=get_vector_db)],
    storage: Annotated[StorageInterface, Depends(dependency=get_storage)],
    queue: Annotated[QueueInterface, Depends(dependency=get_queue_client)],
    index_service: Annotated[IndexService, Depends(dependency=get_index_service)],
) -> DocumentService:
    return DocumentService(vdb=vdb, storage=storage, queue=queue, index_service=index_service)
