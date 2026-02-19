from functools import lru_cache
from typing import Self, Annotated
from fastapi import Depends

from .presidio import get_presidio, PresidioPII


class MaskService:
    def __init__(self: Self, presidio_client: PresidioPII):
        self.presidio_client: PresidioPII = presidio_client

    def mask(self: Self, text: str) -> str:
        return self.presidio_client.mask_pii(text=text)

@lru_cache()
def get_mask_service(presidio: Annotated[PresidioPII, Depends(dependency=get_presidio)]) -> MaskService:
    return MaskService(presidio_client=presidio)
