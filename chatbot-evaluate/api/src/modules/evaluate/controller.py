from fastapi import APIRouter, Depends, status, Form
from typing import Annotated, Literal
from uuid import UUID

from dos_utility.auth import get_admin_user, get_user, User

from .service import EvaluationService, get_evaluation_service
from .dto import SimpleFeedbackResponse, EvaluationResponse, EvaluationAllResponse

router: APIRouter = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post(
    path="/simple-feedback/{query_id}",
    response_model=SimpleFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Simple feedback created successfully"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Query not found"},
        status.HTTP_409_CONFLICT: {"description": "Simple feedback already exists"},
    },
    summary="Create a new simple feedback for the authenticated user",
)
async def simple_feedback(
    query_id: UUID,
    feedback: Annotated[Literal[1, -1], Form(description="1 for OK, -1 for KO")],
    user: Annotated[
        User, Depends(dependency=get_user)
    ],  # Any user can do it, as long as he's the 'owner' of the message
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
) -> SimpleFeedbackResponse:
    return await service.create_simple_feedback(
        user_id=user.id,
        query_id=str(query_id),
        feedback=feedback,
    )


@router.post(
    path="/all/{session_id}",
    response_model=EvaluationAllResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "All evaluations created successfully"
        },
    },
    dependencies=[Depends(dependency=get_admin_user)],
    summary="Evaluate all queries",
)
async def post_evaluate_all(
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
    session_id: UUID,
) -> EvaluationAllResponse:
    return await service.evaluate_all(session_id=session_id)


@router.post(
    path="/{query_id}",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Evaluation created successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Query not found"},
    },
    dependencies=[Depends(dependency=get_admin_user)],
    summary="Evaluate a specific query",
)
async def post_evaluate(
    query_id: UUID,
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
) -> EvaluationResponse:
    return await service.evaluate(query_id=str(query_id))
