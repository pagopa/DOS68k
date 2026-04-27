from pathlib import Path
from typing import Self, Any, Dict, List, Optional


class NlpEngineMock:
    """Mock for presidio_analyzer.nlp_engine.NlpEngine."""

    pass


class NlpEngineProviderMock:
    """Mock for presidio_analyzer.nlp_engine.NlpEngineProvider."""

    def __init__(self: Self, nlp_configuration: Dict[str, Any]) -> None:
        pass

    def create_engine(self: Self) -> NlpEngineMock:
        return NlpEngineMock()


class AnalyzerRegistryMock:
    """Mock for AnalyzerEngine.registry."""

    def __init__(self: Self) -> None:
        self.recognizers: List[Any] = []

    def add_recognizer(self: Self, recognizer: Any) -> None:
        self.recognizers.append(recognizer)


class AnalyzerEngineMock:
    """Mock for presidio_analyzer.AnalyzerEngine."""

    def __init__(
        self: Self,
        nlp_engine: Any = None,
        supported_languages: Optional[List[str]] = None,
        default_score_threshold: float = 0.0,
    ) -> None:
        self.registry: AnalyzerRegistryMock = AnalyzerRegistryMock()
        self.analyze_return_value: List[Any] = []
        self.last_analyze_kwargs: Optional[Dict[str, Any]] = None

    def analyze(
        self: Self,
        text: str,
        language: str,
        entities: List[str],
        allow_list: List[str],
    ) -> List[Any]:
        self.last_analyze_kwargs = {
            "text": text,
            "language": language,
            "entities": entities,
            "allow_list": allow_list,
        }
        return self.analyze_return_value


class FakeLang:
    """Mimics langdetect.language.Language with str() returning just the lang code."""

    def __init__(self: Self, code: str) -> None:
        self.code: str = code

    def __str__(self: Self) -> str:
        return self.code

    def __eq__(self: Self, other: object) -> bool:
        return str(self) == str(other)

    def __hash__(self: Self) -> int:
        return hash(self.code)


class PresidioPIIMock:
    """Mock for PresidioPII used in MaskService tests."""

    def __init__(self: Self) -> None:
        self.mask_pii_called_with: Optional[str] = None
        self.mask_pii_return_value: str = "masked"

    def mask_pii(self: Self, text: str) -> str:
        self.mask_pii_called_with = text
        return self.mask_pii_return_value


class MaskServiceMock:
    """Mock for MaskService used in controller tests."""

    def __init__(self: Self) -> None:
        self.mask_return_value: str = "masked output"

    def mask(self: Self, text: str) -> str:
        return self.mask_return_value


class ConfigPathMock:
    """Mock for pathlib.Path used in __read_presidio_config tests.

    Chains Path(__file__).resolve().parents[3] to return base_dir,
    so that / "config" / "presidio.yaml" resolves to a real temp path.
    """

    def __init__(self: Self, base_dir: Path) -> None:
        self._base_dir: Path = base_dir

    def __call__(self: Self, *args: Any) -> "ConfigPathMock":
        return self

    def resolve(self: Self) -> "ConfigPathMock":
        return self

    @property
    def parents(self: Self) -> "_ParentsIndexer":
        return ConfigPathMock._ParentsIndexer(self._base_dir)

    class _ParentsIndexer:
        def __init__(self: Self, base_dir: Path) -> None:
            self._base_dir: Path = base_dir

        def __getitem__(self: Self, index: int) -> Path:
            return self._base_dir


def detect_langs_error_mock(text: str) -> List[FakeLang]:
    """Mock detect_langs that raises an exception (forces Italian fallback)."""
    raise Exception("langdetect failed")


def detect_langs_italian_mock(text: str) -> List[FakeLang]:
    """Mock detect_langs returning Italian and English."""
    return [FakeLang("en"), FakeLang("it")]


def detect_langs_english_only_mock(text: str) -> List[FakeLang]:
    """Mock detect_langs returning only English."""
    return [FakeLang("en")]


def detect_langs_unsupported_mock(text: str) -> List[FakeLang]:
    """Mock detect_langs returning unsupported language only."""
    return [FakeLang("zh")]


def make_presidio_config() -> Dict[str, Any]:
    """Return a minimal presidio config dict for testing."""
    return {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "it", "model_name": "it_core_news_md"},
            {"lang_code": "en", "model_name": "en_core_web_md"},
        ],
        "ner_model_configuration": {
            "labels_to_ignore": [],
            "model_to_presidio_entity_mapping": {"PER": "PERSON"},
            "low_confidence_score_multiplier": 0.4,
            "low_score_entity_names": [],
            "default_score": 0.8,
        },
        "allow_list": [],
    }


VALID_PRESIDIO_YAML: Dict[str, Any] = {
    "config_presidio": {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_md"}],
        "ner_model_configuration": {
            "labels_to_ignore": [],
            "model_to_presidio_entity_mapping": {},
            "low_confidence_score_multiplier": 0.4,
            "low_score_entity_names": [],
            "default_score": 0.8,
        },
        "allow_list": [],
    }
}
