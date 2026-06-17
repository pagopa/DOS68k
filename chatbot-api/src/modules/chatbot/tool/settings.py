from functools import lru_cache
from typing import Optional, Tuple
from pathlib import Path
from pydantic_settings import (
    BaseSettings,
    YamlConfigSettingsSource,
    PydanticBaseSettingsSource,
)


class YamlSettings(BaseSettings):
    index_id: str
    name: str
    description: str
    similarity_top_k: Optional[int] = None
    qa_prompt: Optional[str] = None
    refine_prompt: Optional[str] = None


@lru_cache
def get_yaml_settings(file: Path) -> YamlSettings:
    class _Settings(YamlSettings):
        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls,
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> Tuple[YamlConfigSettingsSource]:
            return (YamlConfigSettingsSource(settings_cls=cls, yaml_file=file),)

    return _Settings()
