from parsers import ChunkData
from env import get_task_settings, TaskSettings
from models import get_embed_model, BaseEmbedding

from dos_utility.vector_db import ObjectData


class Embedder:
    def __init__(self,
                 provider: str,
                 embed_model_id: str,
                 embed_batch_size: int,
                 embed_dim: int,
                 embed_task: str,
                 embed_retries: int,
                 embed_retry_min_seconds: int,
                 model_api_key: str
                 ):
        self.provider = provider
        self.embed_model_id = embed_model_id
        self.embed_batch_size = embed_batch_size
        self.embed_dim = embed_dim
        self.embed_task = embed_task
        self.embed_retries = embed_retries
        self.embed_retry_min_seconds = embed_retry_min_seconds
        self.model_api_key = model_api_key

        self.embed_model: BaseEmbedding = get_embed_model(
            provider=self.provider,
            model_id=self.embed_model_id,
            embed_batch_size=self.embed_batch_size,
            embed_dim=self.embed_dim,
            task_type=self.embed_task,
            retries=self.embed_retries,
            retry_min_seconds=self.embed_retry_min_seconds,
            api_key=self.model_api_key,
        )
    def transform(self, chunks: list[ChunkData]) -> list[ObjectData]:
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
    

def get_embedder(
    provider: str,
    embed_model_id : str,
    embed_batch_size : int,
    embed_dim : int,
    embed_task : str,
    embed_retries : int,
    embed_retry_min_seconds: int,
    model_api_key: str,
) -> Embedder:
    return Embedder(
        provider = provider,
        embed_model_id= embed_model_id,
        embed_batch_size = embed_batch_size,
        embed_dim = embed_dim,
        embed_task = embed_task,
        embed_retries = embed_retries,
        embed_retry_min_seconds = embed_retry_min_seconds,
        model_api_key=model_api_key
    )