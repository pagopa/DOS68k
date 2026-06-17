import pytest

from src.worker import loaders
from src.worker.loaders import (
    Message,
    Document,
    PDFLoader,
    TextLoader,
    DocumentLoader,
    get_loaders,
    get_document_loader,
)
from test.worker.mocks import StorageMock, PyMuPDFMock


def test_get_loaders():
    result = get_loaders()

    assert "application/pdf" in result
    assert "text/plain" in result
    assert "text/markdown" in result
    assert isinstance(result["application/pdf"], PDFLoader)
    assert isinstance(result["text/plain"], TextLoader)
    assert isinstance(result["text/markdown"], TextLoader)


def test_message_model():
    msg = Message(
        index_id="idx1",
        user_id="user1",
        object_key="doc.pdf",
        document_type="application/pdf",
    )

    assert msg.index_id == "idx1"
    assert msg.user_id == "user1"
    assert msg.object_key == "doc.pdf"
    assert msg.document_type == "application/pdf"


def test_message_model_invalid_document_type():
    with pytest.raises(Exception):
        Message(
            index_id="idx1",
            user_id="user1",
            object_key="doc.pdf",
            document_type="application/xml",
        )


def test_pdf_loader_read(monkeypatch):
    monkeypatch.setattr(loaders, "pymupdf", PyMuPDFMock())

    loader = PDFLoader()
    result = loader.read(data=b"%PDF fake content")

    assert result == ["page content", "page content"]


def test_text_loader_read():
    loader = TextLoader()
    result = loader.read(data=b"hello world")

    assert result == ["hello world"]


def test_document_loader_read(monkeypatch):
    storage_mock = StorageMock(data=b"hello world")
    monkeypatch.setattr(loaders, "get_storage", lambda: storage_mock)

    document_loader = DocumentLoader(bucket_name="test-bucket")
    msg = Message(
        index_id="idx1",
        user_id="user1",
        object_key="doc.txt",
        document_type="text/plain",
    )

    result = document_loader.read(message=msg)

    assert isinstance(result, Document)
    assert result.filename == "doc.txt"
    assert result.content == ["hello world"]


def test_get_document_loader(monkeypatch):
    monkeypatch.setattr(loaders, "get_storage", lambda: StorageMock())
    get_document_loader.cache_clear()

    loader = get_document_loader(bucket_name="test-bucket")

    assert isinstance(loader, DocumentLoader)
    get_document_loader.cache_clear()
