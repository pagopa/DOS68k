from typing import Literal, Optional, List
from llama_index.core.llms.llm import LLM
from dos_utility.utils.logger import get_logger
from logging import Logger

from env import get_global_settings, GlobalSettings

log_settings: GlobalSettings = get_global_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


def get_llm(
    provider: Literal["google"],
    model_id: Optional[str],
    temperature: Optional[float],
    max_tokens: Optional[int],
    api_key: Optional[str],
) -> LLM:
    """Returns an LLM instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google").
        model_id: Override the model ID from SETTINGS.
        temperature: Override the temperature from SETTINGS.
        max_tokens: Override the max tokens from SETTINGS.

    Returns:
        LLM: A LlamaIndex-compatible LLM instance.
    """
    if provider == "google":
        from llama_index.llms.google_genai import GoogleGenAI
        from google.genai.types import (
            GenerateContentConfig,
            HarmCategory,
            HarmBlockThreshold,
            SafetySetting,
        )

        safety_settings: List[SafetySetting] = [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
        ]
        llm: GoogleGenAI = GoogleGenAI(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            generation_config=GenerateContentConfig(safety_settings=safety_settings),
        )
        logger.debug("LLM loaded - provider=google, model_id=%s", model_id)

    return llm