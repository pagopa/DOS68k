from typing import Annotated
from fastapi import APIRouter, Depends

from .service import get_mask_service, MaskService
from .dto import MaskRequestBody

router: APIRouter = APIRouter(prefix="/mask", tags=["Mask"])

@router.post(
    path="",
    response_model=str,
    summary="Mask PII",
)
def mask(
        mask_service: Annotated[MaskService, Depends(dependency=get_mask_service)],
        mask_body: MaskRequestBody,
    ) -> str:
    return mask_service.mask(text=mask_body.text)