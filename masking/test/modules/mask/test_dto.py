import pytest

from pydantic import ValidationError

from src.modules.mask.dto import MaskRequestBody


class TestMaskRequestBody:

    def test_valid(self) -> None:
        """Valid text field is accepted."""
        body: MaskRequestBody = MaskRequestBody(text="Hello world")
        assert body.text == "Hello world"

    def test_missing_text(self) -> None:
        """Missing text field raises ValidationError."""
        with pytest.raises(ValidationError):
            MaskRequestBody()

    def test_extra_fields_ignored(self) -> None:
        """Extra fields are ignored by default (Pydantic default behavior)."""
        body: MaskRequestBody = MaskRequestBody(text="Hello", extra_field="should be ignored")
        assert body.text == "Hello"
        assert not hasattr(body, "extra_field")
