from functools import lru_cache
from logging import Logger

from dos_utility.vector_db import ObjectData
from dos_utility.utils.logger import get_logger

from parsers import ChunkData
from models import get_embed_model, BaseEmbedding
from env import get_global_settings


class Embedder:
    def __init__(
        self,
        provider: str,
        embed_model_id: str,
        embed_batch_size: int,
        embed_dim: int,
        embed_task: str,
        embed_retries: int,
        embed_retry_min_seconds: int,
        model_api_key: str,
    ):
        settings = get_global_settings()
        self._logger: Logger = get_logger(name=__name__, level=settings.log_level)
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

        for idx, chunk in enumerate(chunks):
            if (idx + 1) % max(1, len(chunks) // 10) == 0 or idx == 0:
                self._logger.debug(
                    f"Embedding progress: {idx + 1}/{len(chunks)} chunks"
                )

            embedding = self.embed_model.get_text_embedding(chunk.content)
            embedded_chunks.append(ObjectData(**chunk.model_dump(), vector=embedding))

        return embedded_chunks


@lru_cache
def get_embedder(
    provider: str,
    embed_model_id: str,
    embed_batch_size: int,
    embed_dim: int,
    embed_task: str,
    embed_retries: int,
    embed_retry_min_seconds: int,
    model_api_key: str,
) -> Embedder:
    return Embedder(
        provider=provider,
        embed_model_id=embed_model_id,
        embed_batch_size=embed_batch_size,
        embed_dim=embed_dim,
        embed_task=embed_task,
        embed_retries=embed_retries,
        embed_retry_min_seconds=embed_retry_min_seconds,
        model_api_key=model_api_key,
    )
