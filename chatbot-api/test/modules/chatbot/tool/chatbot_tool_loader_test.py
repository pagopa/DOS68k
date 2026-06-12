from pathlib import Path
from typing import List

import pytest

from dos_utility.agent import RagToolSpec

from src.modules.chatbot.tool.loader import load_rag_tool_specs


def test_load_rag_tool_specs_invalid_custom_file_directory() -> None:
    dir: Path = Path(__file__) / "non_existing_directory"

    with pytest.raises(
        expected_exception=FileNotFoundError,
        match=f"Tool config directory not found: {dir}",
    ):
        load_rag_tool_specs(config_dir=dir)


def test_load_rag_tool_specs_empty_custom_file_directory() -> None:
    dir: Path = Path(__file__).parent / "empty_tool_config_folder"

    specs: List[RagToolSpec] = load_rag_tool_specs(config_dir=dir)

    assert specs == []


def test_load_rag_tool_specs() -> None:
    dir: Path = Path(__file__).parent / "tool_config_folder"

    specs: List[RagToolSpec] = load_rag_tool_specs(config_dir=dir)

    assert len(specs) == 1
    assert isinstance(specs[0], RagToolSpec)
    assert specs[0].name == "RAGToolTest"
