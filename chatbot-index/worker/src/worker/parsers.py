from functools import lru_cache
from typing import Annotated
from pydantic import Field, BaseModel
from llama_index.core.node_parser import SentenceSplitter 
from llama_index.core import Document as RefDocument

from loaders import Document


class ChunkData(BaseModel):
    """Represents a single object to be stored in the vector database. Each object corresponds to a chunk of text from a file."""

    filename: Annotated[
        str, Field(description="The name of the file the object comes from.")
    ]
    chunk_id: Annotated[
        int,
        Field(
            description="The chunk ID within the file. If the file is not chunked set it to 0."
        ),
    ]
    content: Annotated[str, Field(description="The content of the chunk.")]


class Parser:

    def __init__ (self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        print(f"Chunk size: {self.chunk_size} -- overlap: {self.chunk_overlap}")

        self._splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def transform(self, document: Document) -> list[ChunkData]:
        filename = document.filename
        # chunk_content = ["\n".join(document.content)]
        ref_document = RefDocument(text = "\n".join(document.content))
        text_chunks = [x.text for x in self._splitter([ref_document])]
        chunks = []
        for chunk_id, text_chunk in enumerate(text_chunks):
            chunks.append(
                ChunkData(filename=filename, 
                          chunk_id=chunk_id, 
                          content=text_chunk)
            )
        return chunks


@lru_cache
def get_parser( chunk_size: int, chunk_overlap: int) -> Parser:
    return Parser(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
                  )
