from fastapi import APIRouter, Depends, UploadFile, File, status
from typing import List, Annotated

from .dto import UploadDocumentResponse, DocumentInfo
from .service import DocumentService, get_document_service
from ..auth import get_user_id


router: APIRouter = APIRouter(prefix="/index/{index_id}/documents", tags=["documents"])


@router.post(
    path="",
    response_model=UploadDocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "Document uploaded and queued for processing"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Index not found"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": "Unsupported file type. Allowed: .pdf, .md, .txt"
        },
    },
    summary="Upload a document to an index for ingestion",
)
async def upload_document(
    index_id: str,
    file: Annotated[UploadFile, File(description="Document file to upload")],
    service: Annotated[DocumentService, Depends(dependency=get_document_service)],
    user: Annotated[str, Depends(dependency=get_user_id)],
) -> UploadDocumentResponse:
    return await service.upload_document(index_id=index_id, file=file, user=user)


@router.get(
    path="",
    response_model=List[DocumentInfo],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Index not found"},
    },
    dependencies=[Depends(dependency=get_user_id)],
    summary="List all documents in an index",
)
async def list_documents(
    index_id: str,
    service: Annotated[DocumentService, Depends(dependency=get_document_service)],
) -> List[DocumentInfo]:
    return await service.list_documents(index_id=index_id)


@router.delete(
    path="/{document_name}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Document deleted successfully"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Index not found or document not found"
        },
    },
    dependencies=[Depends(dependency=get_user_id)],
    summary="Delete a document from an index",
)
async def delete_document(
    index_id: str,
    document_name: str,
    service: Annotated[DocumentService, Depends(dependency=get_document_service)],
) -> dict:
    await service.delete_document(index_id=index_id, document_name=document_name)
    return {"message": f"Document '{document_name}' deleted from index '{index_id}'"}
