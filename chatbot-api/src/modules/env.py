from functools import lru_cache
from typing import Optional, Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class MaskingSettings(BaseSettings):
    mask_pii: Annotated[bool, Field(default=False)]
    masking_service_url: Annotated[Optional[str], Field(default=None)]

class LogSettings(BaseSettings):
    log_level: Annotated[int, Field(default=20)]  # logging.INFO = 20

@lru_cache
def get_masking_settings() -> MaskingSettings:
    return MaskingSettings()

@lru_cache
def get_logging_settings() -> LogSettings:
    return LogSettings()