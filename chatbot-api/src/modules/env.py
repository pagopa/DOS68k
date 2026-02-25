from functools import lru_cache
from typing import Optional, Annotated
from pydantic import PositiveInt, Field
from pydantic_settings import BaseSettings

class SessionSettings(BaseSettings):
    session_expiration_days: PositiveInt

class MaskingSettings(BaseSettings):
    mask_pii: Annotated[bool, Field(default=False)]
    masking_service_url: Annotated[Optional[str], Field(default=None)]

@lru_cache
def get_session_settings() -> SessionSettings:
    return SessionSettings()

@lru_cache
def get_masking_settings() -> MaskingSettings:
    return MaskingSettings()