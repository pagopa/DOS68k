import pytest
import yaml

from pathlib import Path
from typing import Any, Dict, List

import src.modules.mask.presidio as presidio_mod
from src.modules.mask.presidio import (
    PresidioModelConfig,
    NerModelConfiguration,
    PresidioConfig,
    PresidioYamlConfig,
    EntityTypeCountAnonymizer,
    PresidioPII,
    GLOBAL_ENTITIES,
    IT_ENTITIES,
    get_presidio,
)
from presidio_analyzer import RecognizerResult
from presidio_anonymizer.operators import OperatorType
from pydantic import ValidationError

from test.modules.mask.mocks import (
    NlpEngineProviderMock,
    AnalyzerEngineMock,
    FakeLang,
    ConfigPathMock,
    make_presidio_config,
    detect_langs_error_mock,
    detect_langs_italian_mock,
    detect_langs_english_only_mock,
    detect_langs_unsupported_mock,
    VALID_PRESIDIO_YAML,
)

# Module-level access to avoid name mangling inside class bodies
_read_presidio_config = presidio_mod.__dict__["__read_presidio_config"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def presidio_instance(monkeypatch: pytest.MonkeyPatch) -> PresidioPII:
    """Create a PresidioPII with mocked NLP engine and analyzer."""
    monkeypatch.setattr(presidio_mod, "NlpEngineProvider", NlpEngineProviderMock)
    monkeypatch.setattr(presidio_mod, "AnalyzerEngine", AnalyzerEngineMock)
    config: Dict[str, Any] = make_presidio_config()
    instance: PresidioPII = PresidioPII(config=config)
    return instance


# ---------------------------------------------------------------------------
# Pydantic config models
# ---------------------------------------------------------------------------

class TestPresidioModelConfig:

    def test_valid(self) -> None:
        """Valid PresidioModelConfig is accepted."""
        cfg: PresidioModelConfig = PresidioModelConfig(lang_code="en", model_name="en_core_web_md")
        assert cfg.lang_code == "en"
        assert cfg.model_name == "en_core_web_md"

    def test_extra_field_rejected(self) -> None:
        """Extra fields are rejected (extra='forbid')."""
        with pytest.raises(ValidationError):
            PresidioModelConfig(lang_code="en", model_name="en_core_web_md", extra="bad")


class TestNerModelConfiguration:

    def test_valid(self) -> None:
        """Valid NerModelConfiguration is accepted."""
        cfg: NerModelConfiguration = NerModelConfiguration(
            labels_to_ignore=["ORDINAL"],
            model_to_presidio_entity_mapping={"PER": "PERSON"},
            low_confidence_score_multiplier=0.4,
            low_score_entity_names=["ORG"],
            default_score=0.8,
        )
        assert cfg.default_score == 0.8


class TestPresidioConfig:

    def test_valid(self) -> None:
        """Valid PresidioConfig is accepted."""
        cfg: PresidioConfig = PresidioConfig(
            nlp_engine_name="spacy",
            models=[PresidioModelConfig(lang_code="en", model_name="en_core_web_md")],
            ner_model_configuration=NerModelConfiguration(
                labels_to_ignore=[],
                model_to_presidio_entity_mapping={},
                low_confidence_score_multiplier=0.4,
                low_score_entity_names=[],
                default_score=0.8,
            ),
            allow_list=[],
        )
        assert cfg.nlp_engine_name == "spacy"


class TestPresidioYamlConfig:

    def test_valid(self) -> None:
        """Valid PresidioYamlConfig is accepted."""
        inner: PresidioConfig = PresidioConfig(
            nlp_engine_name="spacy",
            models=[PresidioModelConfig(lang_code="en", model_name="en_core_web_md")],
            ner_model_configuration=NerModelConfiguration(
                labels_to_ignore=[],
                model_to_presidio_entity_mapping={},
                low_confidence_score_multiplier=0.4,
                low_score_entity_names=[],
                default_score=0.8,
            ),
            allow_list=[],
        )
        wrapper: PresidioYamlConfig = PresidioYamlConfig(config_presidio=inner)
        assert wrapper.config_presidio.nlp_engine_name == "spacy"

    def test_missing_config_presidio(self) -> None:
        """Missing config_presidio raises ValidationError."""
        with pytest.raises(ValidationError):
            PresidioYamlConfig()


# ---------------------------------------------------------------------------
# EntityTypeCountAnonymizer
# ---------------------------------------------------------------------------

class TestEntityTypeCountAnonymizer:

    def setup_method(self) -> None:
        self.anonymizer: EntityTypeCountAnonymizer = EntityTypeCountAnonymizer()

    def test_operate_new_entity(self) -> None:
        """First occurrence creates <TYPE_1> placeholder."""
        entity_mapping: Dict[str, Dict] = {}
        deanonymize_mapping: Dict[str, str] = {}
        params: Dict[str, Any] = {
            "entity_type": "PERSON",
            "entity_mapping": entity_mapping,
            "deanonymize_mapping": deanonymize_mapping,
        }

        result: str = self.anonymizer.operate("John Doe", params)
        assert result == "<PERSON_1>"

    def test_operate_existing_entity(self) -> None:
        """Same text returns the same placeholder."""
        entity_mapping: Dict[str, Dict] = {"PERSON": {"John Doe": "<PERSON_1>"}}
        deanonymize_mapping: Dict[str, str] = {"<PERSON_1>": "John Doe"}
        params: Dict[str, Any] = {
            "entity_type": "PERSON",
            "entity_mapping": entity_mapping,
            "deanonymize_mapping": deanonymize_mapping,
        }

        result: str = self.anonymizer.operate("John Doe", params)
        assert result == "<PERSON_1>"

    def test_operate_multiple_entities_same_type(self) -> None:
        """Multiple different values of the same type get incremented indices."""
        entity_mapping: Dict[str, Dict] = {}
        deanonymize_mapping: Dict[str, str] = {}
        params: Dict[str, Any] = {
            "entity_type": "PERSON",
            "entity_mapping": entity_mapping,
            "deanonymize_mapping": deanonymize_mapping,
        }

        result1: str = self.anonymizer.operate("John Doe", params)
        result2: str = self.anonymizer.operate("Jane Smith", params)
        assert result1 == "<PERSON_1>"
        assert result2 == "<PERSON_2>"

    def test_operate_populates_deanonymize_mapping(self) -> None:
        """Reverse mapping is filled correctly."""
        entity_mapping: Dict[str, Dict] = {}
        deanonymize_mapping: Dict[str, str] = {}
        params: Dict[str, Any] = {
            "entity_type": "EMAIL_ADDRESS",
            "entity_mapping": entity_mapping,
            "deanonymize_mapping": deanonymize_mapping,
        }

        self.anonymizer.operate("test@example.com", params)
        assert deanonymize_mapping["<EMAIL_ADDRESS_1>"] == "test@example.com"

    def test_validate_missing_entity_mapping(self) -> None:
        """Missing entity_mapping raises ValueError."""
        with pytest.raises(ValueError, match="entity_mapping"):
            self.anonymizer.validate({"entity_type": "PERSON", "deanonymize_mapping": {}})

    def test_validate_missing_entity_type(self) -> None:
        """Missing entity_type raises ValueError."""
        with pytest.raises(ValueError, match="entity_type"):
            self.anonymizer.validate({"entity_mapping": {}, "deanonymize_mapping": {}})

    def test_validate_missing_deanonymize_mapping(self) -> None:
        """Missing deanonymize_mapping raises ValueError."""
        with pytest.raises(ValueError, match="deanonymize_mapping"):
            self.anonymizer.validate({"entity_mapping": {}, "entity_type": "PERSON"})

    def test_validate_success(self) -> None:
        """No error when all required params are present."""
        self.anonymizer.validate({
            "entity_mapping": {},
            "entity_type": "PERSON",
            "deanonymize_mapping": {},
        })

    def test_operator_name(self) -> None:
        """operator_name returns the class name."""
        assert self.anonymizer.operator_name() == "EntityTypeCountAnonymizer"

    def test_operator_type(self) -> None:
        """operator_type returns OperatorType.Anonymize."""
        assert self.anonymizer.operator_type() == OperatorType.Anonymize


# ---------------------------------------------------------------------------
# PresidioPII
# ---------------------------------------------------------------------------

class TestPresidioPII:

    def test_mask_pii_no_pii(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """Text without PII is returned as-is."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_error_mock)

        result: str = presidio_instance.mask_pii(text="Hello world")
        assert result == "Hello world"

    def test_mask_pii_with_pii(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """Text with PII is masked via EntityTypeCountAnonymizer."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_error_mock)

        recognizer_result: RecognizerResult = RecognizerResult(
            entity_type="PERSON", start=0, end=8, score=0.85,
        )
        analyzer: AnalyzerEngineMock = presidio_instance.analyzer
        analyzer.analyze_return_value = [recognizer_result]

        result: str = presidio_instance.mask_pii(text="John Doe said hello")
        assert "<PERSON_1>" in result
        assert "John Doe" not in result

    def test_detect_language_exception_fallback(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """Exception in langdetect returns 'it'."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_error_mock)

        result: str = presidio_instance._PresidioPII__detect_language("some text")
        assert result == "it"

    def test_detect_language_no_matching_languages(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """When no detected language matches supported languages, fallback to 'it'."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_unsupported_mock)

        result: str = presidio_instance._PresidioPII__detect_language("some text")
        assert result == "it"

    def test_detect_language_italian_preferred(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """When 'it' is among detected languages, it is chosen."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_italian_mock)

        result: str = presidio_instance._PresidioPII__detect_language("testo in italiano")
        assert result == "it"

    def test_detect_language_non_italian_supported(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """Non-Italian supported language is returned when 'it' is not detected."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_english_only_mock)

        result = presidio_instance._PresidioPII__detect_language("english text")
        assert str(result) == "en"

    def test_detect_pii_adds_italian_entities(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """When language is 'it', IT_ENTITIES are included in analysis."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_error_mock)

        presidio_instance._PresidioPII__detect_pii("testo italiano")

        analyzer: AnalyzerEngineMock = presidio_instance.analyzer
        assert analyzer.last_analyze_kwargs is not None
        entities: List[str] = analyzer.last_analyze_kwargs["entities"]
        for it_entity in IT_ENTITIES:
            assert it_entity in entities

    def test_detect_pii_non_italian(self, monkeypatch: pytest.MonkeyPatch, presidio_instance: PresidioPII) -> None:
        """Non-IT language uses only GLOBAL_ENTITIES."""
        monkeypatch.setattr(presidio_mod, "detect_langs", detect_langs_english_only_mock)

        presidio_instance._PresidioPII__detect_pii("english text")

        analyzer: AnalyzerEngineMock = presidio_instance.analyzer
        assert analyzer.last_analyze_kwargs is not None
        entities: List[str] = analyzer.last_analyze_kwargs["entities"]
        assert entities == GLOBAL_ENTITIES


# ---------------------------------------------------------------------------
# __read_presidio_config
# ---------------------------------------------------------------------------

class TestReadPresidioConfig:

    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        _read_presidio_config.cache_clear()
        yield
        _read_presidio_config.cache_clear()

    def test_file_not_found(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Missing config file raises RuntimeError."""
        monkeypatch.setattr(presidio_mod, "Path", ConfigPathMock(tmp_path))

        with pytest.raises(RuntimeError, match="not found"):
            _read_presidio_config()

    def test_invalid_yaml(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Invalid YAML raises RuntimeError."""
        config_dir: Path = tmp_path / "config"
        config_dir.mkdir()
        config_file: Path = config_dir / "presidio.yaml"
        config_file.write_text("{")

        monkeypatch.setattr(presidio_mod, "Path", ConfigPathMock(tmp_path))

        with pytest.raises(RuntimeError, match="Invalid YAML"):
            _read_presidio_config()

    def test_invalid_schema(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Invalid schema raises RuntimeError."""
        config_dir: Path = tmp_path / "config"
        config_dir.mkdir()
        config_file: Path = config_dir / "presidio.yaml"
        config_file.write_text(yaml.dump({"bad_key": "bad_value"}))

        monkeypatch.setattr(presidio_mod, "Path", ConfigPathMock(tmp_path))

        with pytest.raises(RuntimeError, match="Invalid Presidio config schema"):
            _read_presidio_config()

    def test_yaml_returns_none(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Empty YAML file (None) triggers raw={} fallback and then schema error."""
        config_dir: Path = tmp_path / "config"
        config_dir.mkdir()
        config_file: Path = config_dir / "presidio.yaml"
        config_file.write_text("")

        monkeypatch.setattr(presidio_mod, "Path", ConfigPathMock(tmp_path))

        with pytest.raises(RuntimeError, match="Invalid Presidio config schema"):
            _read_presidio_config()

    def test_valid(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Valid config returns dict with expected keys."""
        config_dir: Path = tmp_path / "config"
        config_dir.mkdir()
        config_file: Path = config_dir / "presidio.yaml"
        config_file.write_text(yaml.dump(VALID_PRESIDIO_YAML))

        monkeypatch.setattr(presidio_mod, "Path", ConfigPathMock(tmp_path))

        result: Dict[str, Any] = _read_presidio_config()
        assert result["nlp_engine_name"] == "spacy"
        assert "models" in result


# ---------------------------------------------------------------------------
# get_presidio
# ---------------------------------------------------------------------------

class TestGetPresidio:

    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        get_presidio.cache_clear()
        _read_presidio_config.cache_clear()
        yield
        get_presidio.cache_clear()
        _read_presidio_config.cache_clear()

    def test_returns_presidio_pii(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_presidio returns a PresidioPII instance."""
        mock_config: Dict[str, Any] = make_presidio_config()

        monkeypatch.setattr(presidio_mod, "__read_presidio_config", lambda: mock_config)
        monkeypatch.setattr(presidio_mod, "NlpEngineProvider", NlpEngineProviderMock)
        monkeypatch.setattr(presidio_mod, "AnalyzerEngine", AnalyzerEngineMock)

        result: PresidioPII = get_presidio()
        assert isinstance(result, PresidioPII)
