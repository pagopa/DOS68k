import yaml

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Self, Optional
from langdetect import detect_langs
from langdetect.language import Language
from pydantic import BaseModel, ConfigDict, ValidationError
from presidio_anonymizer.operators import Operator, OperatorType
from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
from presidio_anonymizer import AnonymizerEngine, EngineResult
from presidio_anonymizer.entities import OperatorConfig


class PresidioModelConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")

    lang_code: str
    model_name: str


class NerModelConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    labels_to_ignore: List[str]
    model_to_presidio_entity_mapping: Dict[str, str]
    low_confidence_score_multiplier: float
    low_score_entity_names: List[str]
    default_score: float


class PresidioConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")

    nlp_engine_name: str
    models: List[PresidioModelConfig]
    ner_model_configuration: NerModelConfiguration
    allow_list: List[str]


class PresidioYamlConfig(BaseModel):
    """YAML wrapper matching `masking/config/presidio.yaml`."""

    model_config: ConfigDict = ConfigDict(extra="forbid")

    config_presidio: PresidioConfig


class EntityTypeCountAnonymizer(Operator):
    """
    Anonymizer which replaces the entity value
    with an type counter per entity.
    """

    REPLACING_FORMAT = "<{entity_type}_{index}>"

    def operate(self: Self, text: str, params: Dict[str, Any]) -> str:
        """Anonymize the input text."""
        entity_type: str = params["entity_type"]
        entity_mapping: Dict[str, Dict] = params["entity_mapping"]
        deanonymize_mapping: Dict[str, str] = params["deanonymize_mapping"]

        entity_mapping_for_type: Optional[Dict] = entity_mapping.get(entity_type)

        if entity_mapping_for_type is None:
            entity_mapping_for_type = entity_mapping[entity_type] = {}

        if text in entity_mapping_for_type:
            return entity_mapping_for_type[text]

        new_text: str = self.REPLACING_FORMAT.format(
            entity_type=entity_type,
            index=len(entity_mapping_for_type) + 1,
        )
        entity_mapping[entity_type][text] = new_text
        deanonymize_mapping[new_text] = text

        return new_text

    def validate(self, params: Dict[str, Any]) -> None:
        """Validate operator parameters."""
        if "entity_mapping" not in params:
            raise ValueError("An input Dict called `entity_mapping` is required.")
        if "entity_type" not in params:
            raise ValueError("An entity_type param is required.")
        if "deanonymize_mapping" not in params:
            raise ValueError("A deanonymize_mapping param is required.")

    def operator_name(self) -> str:
        return self.__class__.__name__

    def operator_type(self) -> OperatorType:
        return OperatorType.Anonymize


# see supported entities by Presidio with their description at:
# https://microsoft.github.io/presidio/supported_entities/
GLOBAL_ENTITIES: List[str] = [
    "CREDIT_CARD",
    "CRYPTO",
    "DATE_TIME",
    "EMAIL_ADDRESS",
    "IBAN_CODE",
    "IP_ADDRESS",
    "NRP",
    "LOCATION",
    "PERSON",
    "PHONE_NUMBER",
    "MEDICAL_LICENSE",
]

IT_ENTITIES: List[str] = [
    "IT_FISCAL_CODE",
    "IT_DRIVER_LICENSE",
    "IT_VAT_CODE",
    "IT_PASSPORT",
    "IT_IDENTITY_CARD",
    "IT_PHYSICAL_ADDRESS",
]


class PresidioPII:
    def __init__(
        self: Self,
        config: PresidioConfig | Dict[str, Any],
        analyzer_threshold: float = 0.4,
        entities: Optional[List[str]] = None,
        mapping: Optional[Dict[str, str]] = None,
        entity_mapping: Optional[Dict[str, Dict]] = None,
    ):
        self.config: Dict[str, Any] = (
            config.model_dump() if isinstance(config, PresidioConfig) else config
        )
        self.languages: List[str] = [
            item["lang_code"] for item in self.config["models"]
        ]
        self.entities: List[str] = entities if entities is not None else GLOBAL_ENTITIES
        self.entity_mapping = entity_mapping if entity_mapping is not None else {}
        self.mapping = mapping if mapping is not None else {}
        self.provider: NlpEngineProvider = NlpEngineProvider(
            nlp_configuration=self.config
        )
        self.nlp_engine: NlpEngine = self.provider.create_engine()
        self.analyzer: AnalyzerEngine = AnalyzerEngine(
            nlp_engine=self.nlp_engine,
            supported_languages=self.languages,
            default_score_threshold=analyzer_threshold,
        )
        self.__add_italian_physical_address_entity()
        self.engine = AnonymizerEngine()
        self.engine.add_anonymizer(EntityTypeCountAnonymizer)

    def __add_italian_physical_address_entity(self: Self) -> None:
        italian_address_pattern: Pattern = Pattern(
            name="italian_address_pattern",
            regex=r"\b(via|viale|piazza|corso|vicolo)\s+[A-Za-z\s]+\s*\d{1,4}.*\b",
            score=0.8,
        )
        address_recognizer: PatternRecognizer = PatternRecognizer(
            supported_entity="IT_PHYSICAL_ADDRESS",
            patterns=[italian_address_pattern],
            supported_language="it",
        )

        self.analyzer.registry.add_recognizer(recognizer=address_recognizer)

    def __detect_language(self: Self, text: str) -> str:
        language_list: List[Language] = []

        try:
            detected_languages: List[Language] = detect_langs(text=text)
        except Exception:
            return "it"

        for detected_language in detected_languages:
            if str(detected_language) in self.languages:
                language_list.append(detected_language)

        if len(language_list) == 0:
            return "it"
        elif "it" in language_list:
            return "it"

        return language_list[0]

    def __detect_pii(self: Self, text: str) -> List[RecognizerResult]:
        lang: str = self.__detect_language(text=text)
        results: List[RecognizerResult] = self.analyzer.analyze(
            text=text,
            language=lang,
            entities=self.entities + IT_ENTITIES if lang == "it" else self.entities,
            allow_list=self.config["allow_list"],
        )

        return results

    def mask_pii(self: Self, text: str) -> str:
        results: List[RecognizerResult] = self.__detect_pii(text=text)
        new_text: EngineResult = self.engine.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig(
                    operator_name="EntityTypeCountAnonymizer",
                    params={
                        "entity_mapping": self.entity_mapping,
                        "deanonymize_mapping": self.mapping,
                    },
                ),
            },
        )

        return new_text.text


@lru_cache()
def __read_presidio_config() -> Dict[str, Any]:
    config_path: Path = Path(__file__).resolve().parents[3] / "config" / "presidio.yaml"

    try:
        with config_path.open(mode="r", encoding="utf-8") as f:
            raw: Any = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Presidio config file not found: {config_path}") from e
    except yaml.YAMLError as e:
        raise RuntimeError(
            f"Invalid YAML in Presidio config file: {config_path}"
        ) from e

    if raw is None:
        raw = {}

    try:
        parsed: PresidioYamlConfig = PresidioYamlConfig.model_validate(obj=raw)
    except ValidationError as e:
        raise RuntimeError(
            "Invalid Presidio config schema "
            f"(file: {config_path}). Validation errors:\n{e}"
        ) from e

    # Return the inner structure Presidio expects (nlp_engine_name/models/...)
    return parsed.config_presidio.model_dump()


@lru_cache()
def get_presidio() -> PresidioPII:
    # Leggy YAML configurazione
    presidio_config: Dict[str, Any] = __read_presidio_config()

    return PresidioPII(config=presidio_config)
