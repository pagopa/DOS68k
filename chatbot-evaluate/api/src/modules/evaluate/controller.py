from fastapi import APIRouter, Depends, status
from typing import List, Annotated
from .service import EvaluationService, get_evaluation_service
from ..auth import get_user_id
from .dto import SimpleFeedbackResponse

router: APIRouter = APIRouter(prefix="/evaluate", tags=["evaluate"])

@router.post(
    path="/simple-feedback/{query_id}",
    response_model=SimpleFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Simple feedback created successfully"},
        status.HTTP_409_CONFLICT: {"description": "Simple feedback already exists"},
    },
    summary="Create a new simple feedback for the authenticated user",
)
async def post_simple_feedback(
    query_id: str,
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
) -> SimpleFeedbackResponse:
    return await service.create_simple_feedback(query_id=query_id)