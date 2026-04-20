from logging import Logger
from typing import Self, Annotated
from fastapi import Depends

from dos_utility.utils import logger
from dos_utility.storage import StorageInterface, get_storage

from ...env import (
    get_settings,
    Settings,
)


class EvaluationService:
    def __init__(self: Self, storage: StorageInterface):
        self.storage: StorageInterface = storage
        self.settings: Settings = get_settings()
        self.logger: Logger = logger.get_logger(__name__)


    async def create_simple_feedback(self, query_id: str) -> dict:
        self.logger.info(f"Creating simple feedback for query_id: {query_id}")
        
        return {"query_id": query_id, "status": "created"}


def get_evaluation_service(
    storage: Annotated[StorageInterface, Depends(dependency=get_storage)],
) -> EvaluationService:
    return EvaluationService(storage=storage)