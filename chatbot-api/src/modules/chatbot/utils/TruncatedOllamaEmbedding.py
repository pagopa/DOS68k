from logging import Logger
from typing import Any, List, Optional

from llama_index.core.bridge.pydantic import Field
from llama_index.embeddings.ollama import OllamaEmbedding

from dos_utility.utils.logger import get_logger
from ...env import get_logging_settings, LogSettings

log_settings: LogSettings = get_logging_settings()

logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


class TruncatedOllamaEmbedding(OllamaEmbedding):
    max_dim: Optional[int] = Field(
        default=None,
        description="Maximum dimension of the embedding."
    )

    def __init__(
            self,
            model_name: str,
            max_dim: Optional[int] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(model_name=model_name, **kwargs)
        self.max_dim = max_dim
        logger.debug(f"Initialized TruncatedOllamaEmbedding: {model_name}, {max_dim}")

    def get_general_text_embedding(self, texts: str) -> List[float]:
        embedding = super().get_general_text_embedding(texts)
        logger.debug(f"get_general_text_embedding: {texts} --> {embedding}")

        if self.max_dim is not None:
            return embedding[:self.max_dim]
        return embedding

    async def aget_general_text_embedding(self, prompt: str) -> List[float]:
        embedding = await super().aget_general_text_embedding(prompt)
        if self.max_dim is not None:
            return embedding[:self.max_dim]
        return embedding

    def get_general_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = super().get_general_text_embeddings(texts)
        if self.max_dim is not None:
            return [emb[:self.max_dim] for emb in embeddings]
        return embeddings

    async def aget_general_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = await super().aget_general_text_embeddings(texts)
        if self.max_dim is not None:
            return [emb[:self.max_dim] for emb in embeddings]
        return embeddings
