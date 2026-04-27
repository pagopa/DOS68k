import pytest

from pathlib import Path
from typing import Dict
from llama_index.core.tools import QueryEngineTool

from src.modules.chatbot.tool import loader
from src.modules.chatbot.tool.loader import load_tools

from test.modules.chatbot.mocks import GoogleGenAIMock, GoogleGenAIEmbeddingMock
from test.modules.chatbot.tool.mocks import get_vector_db_instance_mock


def test_load_tools_invalid_custom_file_directory():
    dir: Path = Path(__file__) / "non_existing_directory"

    with pytest.raises(
        expected_exception=FileNotFoundError,
        match=f"Tool config directory not found: {dir}",
    ):
        load_tools(
            llm=GoogleGenAIMock(),
            embed_model=GoogleGenAIEmbeddingMock(),
            config_dir=dir,
        )


def test_load_tools_empty_custom_file_directory():
    dir: Path = Path(__file__).parent / "empty_tool_config_folder"
    tools: Dict[str, QueryEngineTool] = load_tools(
        llm=GoogleGenAIMock(),
        embed_model=GoogleGenAIEmbeddingMock(),
        config_dir=dir,
    )

    assert tools == {}


def test_load_tools(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(loader, "get_vector_db_instance", get_vector_db_instance_mock)

    dir: Path = Path(__file__).parent / "tool_config_folder"
    tools: Dict[str, QueryEngineTool] = load_tools(
        llm=GoogleGenAIMock(),
        embed_model=GoogleGenAIEmbeddingMock(),
        config_dir=dir,
    )

    assert len(tools.keys()) == 1
    assert isinstance(tools["RAGToolTest"], QueryEngineTool)
