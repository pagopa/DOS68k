from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import Annotated
from uuid import UUID

from dos_utility.auth import get_admin_user, get_user, User

from .service import EvaluationService, get_evaluation_service
from .dto import SimpleFeedbackResponse, EvaluationResponse, EvaluationAllResponse

router: APIRouter = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post(
    path="/simple-feedback/{session_id}/{query_id}",
    response_model=SimpleFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Simple feedback created successfully"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Session or query not found"},
    },
    summary="Create a new simple feedback for the authenticated user",
)
async def simple_feedback(
    session_id: UUID,
    query_id: UUID,
    feedback: Annotated[int, Form(description="1 for OK, -1 for KO")],
    user: Annotated[User, Depends(dependency=get_user)],
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
) -> SimpleFeedbackResponse:
    if feedback not in (1, -1):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="feedback must be 1 (OK) or -1 (KO)",
        )

    return await service.create_simple_feedback(
        user_id=user.id,
        session_id=session_id,
        query_id=query_id,
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
    path="/{session_id}/{query_id}",
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
    session_id: UUID,
    query_id: UUID,
    service: Annotated[EvaluationService, Depends(dependency=get_evaluation_service)],
) -> EvaluationResponse:
    return await service.evaluate(session_id=session_id, query_id=query_id)
