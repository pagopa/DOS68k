from parsers import ChunkData
from env import get_task_settings, TaskSettings
from models import get_embed_model, BaseEmbedding

from dos_utility.vector_db import ObjectData


class Embedder:
    def __init__(self,):
        self.__settings:  TaskSettings = get_task_settings()
        self.embed_model: BaseEmbedding = get_embed_model(
            provider=self.__settings.provider,
            model_id=self.__settings.embed_model_id,
            embed_batch_size=self.__settings.embed_batch_size,
            embed_dim=self.__settings.embed_dim,
            task_type=self.__settings.embed_task,
            retries=self.__settings.embed_retries,
            retry_min_seconds=self.__settings.embed_retry_min_seconds,
            api_key=self.__settings.model_api_key,
        )
    def __call__(self, chunks: list[ChunkData]) -> list[ObjectData]:
        embedded_chunks = []
        for chunk in chunks:
            embedding = self.embed_model.get_text_embedding(chunk.content)
            embedded_chunks.append(
                ObjectData(
                    **chunk.model_dump(),
                    vector = embedding
                )
            )
        return embedded_chunks
    

def get_embedder() -> Embedder:
    return Embedder()