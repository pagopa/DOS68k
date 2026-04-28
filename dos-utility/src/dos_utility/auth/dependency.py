from dataclasses import dataclass
from fastapi import Header, Depends, HTTPException, status
from typing import Annotated
from uuid import UUID
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    id: str
    role: UserRole


def get_user(
    x_user_id: Annotated[UUID, Header()],
    x_user_role: Annotated[UserRole, Header()],
) -> User:
    """FastAPI dependency to get logged user infos.

    Args:
        x_user_id (UUID): id of the user
        x_user_role ("admin" | "user"): role of the user

    Return:
        User: user object with id and role
    """
    return User(id=str(x_user_id), role=x_user_role)

def get_admin_user(user: Annotated[User, Depends(dependency=get_user)]) -> User:
    """Get user and verify if he has admin role. If not, throw a 403 exception.

    Args:
        user (User): logged user

    Raises:
        HTTPException: 403 if user has not admin privileges

    Return:
        User: logged user
    """
    if user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    return user