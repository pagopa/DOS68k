import pytest

from src.worker import parsers
from src.worker.parsers import ChunkData, Parser, get_parser
from src.worker.loaders import Document

from test.worker.mocks import SentenceSplitterMock


def test_chunk_data_model():
    chunk = ChunkData(filename="doc.pdf", chunk_id=0, content="text content")

    assert chunk.filename == "doc.pdf"
    assert chunk.chunk_id == 0
    assert chunk.content == "text content"


def test_parser_transform(monkeypatch):
    monkeypatch.setattr(parsers, "SentenceSplitter", SentenceSplitterMock)

    parser = Parser(chunk_size=512, chunk_overlap=50)
    document = Document(filename="doc.pdf", content=["page 1", "page 2"])

    result = parser.transform(document=document)

    assert len(result) == 2
    assert all(isinstance(c, ChunkData) for c in result)
    assert result[0].filename == "doc.pdf"
    assert result[0].chunk_id == 0
    assert result[0].content == "chunk 1"
    assert result[1].chunk_id == 1
    assert result[1].content == "chunk 2"


def test_get_parser(monkeypatch):
    monkeypatch.setattr(parsers, "SentenceSplitter", SentenceSplitterMock)
    get_parser.cache_clear()

    parser = get_parser(chunk_size=512, chunk_overlap=50)

    assert isinstance(parser, Parser)
    get_parser.cache_clear()
