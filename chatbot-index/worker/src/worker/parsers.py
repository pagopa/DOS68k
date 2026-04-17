from typing import Annotated
from pydantic import Field, BaseModel

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
    def transform(self, document: Document) -> list[ChunkData]:
        filename = document.filename
        chunk_content = ["\n".join(document.content)]
        chunks = []
        for chunk_id, chunk in enumerate(chunk_content):
            chunks.append(
                ChunkData(filename=filename, chunk_id=chunk_id, content=chunk)
            )
        return chunks


def get_parser() -> Parser:
    return Parser()
