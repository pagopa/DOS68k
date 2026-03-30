from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional
from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.tools import QueryEngineTool
from dos_utility.vector_db import VectorDBInterface, get_vector_db_instance
from dos_utility.utils.logger import get_logger

from .settings import get_yaml_settings, YamlSettings
from .factory import get_query_engine_tool
from .vector_index import load_index
from ...env import get_logging_settings, LogSettings

log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)

DEFAULT_CONFIG_DIR: Path = Path(__file__).parent / "config"

def load_tools(
        llm: LLM,
        embed_model: BaseEmbedding,
        similarity_top_k: int = 5,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        use_async: bool = True,
        config_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> Dict[str, QueryEngineTool]:
    """Loads all RAG tools from YAML config files in config_dir.

    Args:
        llm: The language model to use for all tools.
        embed_model: The embedding model to use for all tools.
        similarity_top_k: Number of top results to retrieve per query.
        node_postprocessors: Optional list of postprocessors (e.g. rerankers) applied to all tools.
        use_async: Whether to use async query engine.
        config_dir: Directory containing YAML tool configs. Defaults to tool/config/.
        verbose: Whether to enable verbose logging in retrievers.

    Returns:
        Mapping of tool name to QueryEngineTool, one entry per YAML file.

    Raises:
        FileNotFoundError: If config_dir does not exist.
        ValueError: If no YAML configs are found in config_dir.
    """
    resolved_dir: Path = config_dir or DEFAULT_CONFIG_DIR

    if not resolved_dir.exists():
        raise FileNotFoundError(f"Tool config directory not found: {resolved_dir}")

    # List all YAML files
    yaml_files: List[Path] = sorted(f for f in resolved_dir.glob("*.yaml") if f.name != "template.yaml")

    if len(yaml_files) == 0:
        logger.warning(f"No YAML tool configs found in: {resolved_dir}")

    tools: Dict[str, QueryEngineTool] = {}

    logger.debug("Found %d tool config(s) in %s", len(yaml_files), resolved_dir)

    # For each YAML file create a custom RAG tool
    for yaml_file in yaml_files:
        config: YamlSettings = get_yaml_settings(file=yaml_file) # Get each YAML file through Pydantic Settings
        logger.debug(
            "Loading tool %r - index_id=%s, similarity_top_k=%s, has_qa_prompt=%s, has_refine_prompt=%s",
            config.name, config.index_id, config.similarity_top_k, config.qa_prompt is not None, config.refine_prompt is not None,
        )
        qa_template: PromptTemplate = (
            PromptTemplate(
                template=config.qa_prompt,
                template_var_mappings={
                    "context_str": "context_str",
                    "query_str": "query_str",
                },
            )
            if config.qa_prompt
            else None
        )
        refine_template: PromptTemplate = (
            PromptTemplate(
                template=config.refine_prompt,
                prompt_type="refine",
                template_var_mappings={
                    "existing_answer": "existing_answer",
                    "context_msg": "context_msg",
                },
            )
            if config.refine_prompt
            else None
        )

        vector_db: VectorDBInterface = get_vector_db_instance(index_name=config.index_id)
        index: VectorStoreIndex = load_index(vector_db=vector_db, embed_model=embed_model)
        tool: QueryEngineTool = get_query_engine_tool(
            index=index,
            name=config.name,
            description=config.description,
            llm=llm,
            embed_model=embed_model,
            similarity_top_k=config.similarity_top_k or similarity_top_k,
            text_qa_template=qa_template,
            refine_template=refine_template,
            node_postprocessors=node_postprocessors,
            use_async=use_async,
            verbose=verbose,
        )
        tools[config.name] = tool
        logger.debug("Tool %r loaded successfully", config.name)

    logger.debug("Total tools loaded: %d - %s", len(tools), list(tools.keys()))
    return tools
