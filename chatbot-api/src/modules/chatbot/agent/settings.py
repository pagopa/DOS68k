from functools import lru_cache
from typing import Optional, Tuple
from pathlib import Path
from pydantic_settings import BaseSettings, YamlConfigSettingsSource, PydanticBaseSettingsSource

class AgentYamlSettings(BaseSettings):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    system_header: Optional[str] = None


@lru_cache
def get_agent_yaml_settings(file: Path) -> AgentYamlSettings:
    class _Settings(AgentYamlSettings):
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