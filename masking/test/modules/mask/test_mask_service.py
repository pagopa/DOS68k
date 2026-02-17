from src.modules.mask.service import MaskService, get_mask_service

from test.modules.mask.mocks import PresidioPIIMock


class TestMaskService:

    def test_mask_delegates_to_presidio(self) -> None:
        """MaskService.mask delegates to PresidioPII.mask_pii."""
        mock_presidio: PresidioPIIMock = PresidioPIIMock()
        mock_presidio.mask_pii_return_value = "masked text"

        service: MaskService = MaskService(presidio_client=mock_presidio)
        result: str = service.mask(text="original text")

        assert mock_presidio.mask_pii_called_with == "original text"
        assert result == "masked text"

    def test_mask_returns_string(self) -> None:
        """MaskService.mask returns a string."""
        mock_presidio: PresidioPIIMock = PresidioPIIMock()

        service: MaskService = MaskService(presidio_client=mock_presidio)
        result: str = service.mask(text="some text")

        assert isinstance(result, str)


class TestGetMaskService:

    def test_returns_mask_service(self) -> None:
        """get_mask_service factory returns a MaskService instance."""
        get_mask_service.cache_clear()

        mock_presidio: PresidioPIIMock = PresidioPIIMock()
        result: MaskService = get_mask_service(presidio=mock_presidio)

        assert isinstance(result, MaskService)

        get_mask_service.cache_clear()
