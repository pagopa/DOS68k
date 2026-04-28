from functools import lru_cache
from typing import Annotated, BinaryIO, Literal
from pydantic import Field, BaseModel
import pymupdf

from dos_utility.storage import get_storage


def get_loaders():
    return {"application/pdf": PDFLoader(), "text/plain": TextLoader(), "text/markdown": TextLoader()}


class Message(BaseModel):
    """Task message retrieved from the queue."""

    indexId: Annotated[str, Field(description="Vector db index to add the document")]
    userId: Annotated[str, Field(description="User id")]
    objectKey: Annotated[
        str, Field(description="Key of the document to store on the vector db")
    ]
    documentType: Annotated[
        Literal["application/pdf", "text/markdown", "text/plain"],
        Field(description="Type of document to store on the vector db")
    ]


class Document(BaseModel):
    """Retrieved object from storage."""

    filename: Annotated[
        str, Field(description="The name of the file the object comes from.")
    ]
    content: Annotated[
        list[str], Field(description="Content of each page of the object")
    ]


class PDFLoader:
    def read(self, data: BinaryIO):
        document = pymupdf.open(stream=data)
        content = [
            document.load_page(number).get_text()
            for number in range(document.page_count)
        ]
        return content


class TextLoader:
    def read(self, data: BinaryIO):
        return [data.decode()]


class DocumentLoader:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._storage = get_storage()
        self._loaders = get_loaders()

    def read(self, message: Message) -> Document:
        doc_type = message.documentType
        filename = message.objectKey
        loader = self._loaders[doc_type]
        data = self._storage.get_object(bucket=self.bucket_name, name=filename)
        content = loader.read(data)

        document = Document(filename=filename, content=content)
        return document


@lru_cache
def get_document_loader(bucket_name: str) -> DocumentLoader:
    return DocumentLoader(bucket_name=bucket_name)
