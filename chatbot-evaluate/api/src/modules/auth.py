from fastapi import Header
from uuid import UUID
from typing import Annotated


def get_user_id(x_user_id: Annotated[UUID, Header()]) -> str:
    return str(x_user_id)