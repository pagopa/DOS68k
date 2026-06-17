from logging import Logger
from pathlib import Path
from typing import List

from dos_utility.agent import RagToolSpec
from dos_utility.utils.logger import get_logger

from .settings import YamlSettings, get_yaml_settings
from ...env import LogSettings, get_logging_settings


log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


def load_rag_tool_specs(config_dir: Path) -> List[RagToolSpec]:
    """Read every YAML config in `config_dir` and return matching RagToolSpec entries.

    The YAML files describe the RAG tools the agent can call. The actual
    materialisation of these specs into provider-specific tools is performed
    inside `dos_utility.agent` when the agent client is built.

    Args:
        config_dir: Directory containing YAML tool configs. `template.yaml` is ignored.

    Returns:
        List of `RagToolSpec` entries in alphabetical order of the source filenames.

    Raises:
        FileNotFoundError: If `config_dir` does not exist.
    """
    if not config_dir.exists():
        raise FileNotFoundError(f"Tool config directory not found: {config_dir}")

    yaml_files: List[Path] = sorted(
        f for f in config_dir.glob("*.yaml") if f.name != "template.yaml"
    )

    if len(yaml_files) == 0:
        logger.warning(f"No YAML tool configs found in: {config_dir}")

    logger.debug("Found %d tool config(s) in %s", len(yaml_files), config_dir)

    specs: List[RagToolSpec] = []
    for yaml_file in yaml_files:
        config: YamlSettings = get_yaml_settings(file=yaml_file)
        specs.append(
            RagToolSpec(
                index_id=config.index_id,
                name=config.name,
                description=config.description,
                similarity_top_k=config.similarity_top_k,
                qa_prompt=config.qa_prompt,
                refine_prompt=config.refine_prompt,
            )
        )
        logger.debug("Loaded tool spec %r", config.name)

    logger.debug("Total tool specs loaded: %d", len(specs))
    return specs
