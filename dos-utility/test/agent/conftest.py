import sys
from unittest.mock import MagicMock

# `_models.py` in each provider is the only file that imports optional extras
# (llama-index-llms-openai, llama-index-llms-google-genai, google-genai).
# Stub those internal modules so that the provider __init__.py can be imported
# during test collection without the extras being installed.
#
# Stubbing the internal modules (not the optional packages themselves) keeps
# the real llama_index.core namespace intact, which the instrumentation tests
# rely on via MockLLM.
_STUB_MODULES = [
    "dos_utility.agent.llamaindex_openai._models",
    "dos_utility.agent.llamaindex_google._models",
]

for _mod_name in _STUB_MODULES:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = MagicMock()
