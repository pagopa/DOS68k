"""Stable, short config-hash helpers for trace metadata.

Each helper returns the first 12 hex characters of a SHA-256 digest over
the relevant configuration source. Results are cached for the process
lifetime via ``@lru_cache`` — config is read once at first use.

Paths are read from ``AGENT_CONFIG_PATH`` and ``TOOLS_CONFIG_DIR``,
falling back to the module-bundled defaults. Deliberately independent
of ``ChatbotSettings`` so test environments without the full LLM
configuration can still exercise the metadata pipeline.
"""

import os
from functools import lru_cache
from hashlib import sha256
from pathlib import Path


_HASH_PREFIX_LEN: int = 12
_MODULE_DIR: Path = Path(__file__).parent
_DEFAULT_AGENT_PATH: Path = _MODULE_DIR / "agent" / "agent.yaml"
_DEFAULT_TOOLS_DIR: Path = _MODULE_DIR / "tool" / "config"


def _short_hash(data: bytes) -> str:
    return sha256(data).hexdigest()[:_HASH_PREFIX_LEN]


@lru_cache
def get_agent_config_hash() -> str:
    """First 12 hex chars of SHA-256 over the agent YAML file."""
    path = Path(os.environ.get("AGENT_CONFIG_PATH", _DEFAULT_AGENT_PATH))
    return _short_hash(path.read_bytes())


@lru_cache
def get_tool_config_hash() -> str:
    """First 12 hex chars of SHA-256 over the concatenated bytes of all
    YAML files under ``TOOLS_CONFIG_DIR`` in sorted-name order."""
    root = Path(os.environ.get("TOOLS_CONFIG_DIR", _DEFAULT_TOOLS_DIR))
    files = sorted(p for p in root.iterdir() if p.suffix in {".yaml", ".yml"})
    payload = b"".join(p.read_bytes() for p in files)
    return _short_hash(payload)
