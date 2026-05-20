"""Resolve the chatbot-api package version at module load.

Reads ``pyproject.toml`` at the repository root. Falls back to
``"unknown"`` if the file is unreadable — version is observability
metadata, not load-bearing.
"""

import tomllib
from pathlib import Path


def _resolve_version() -> str:
    try:
        pyproject = Path(__file__).resolve().parents[3] / "pyproject.toml"
        with pyproject.open("rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "unknown"


CHATBOT_API_VERSION: str = _resolve_version()
