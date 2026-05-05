import pytest

from uuid import UUID
from fastapi import HTTPException

from dos_utility.auth.dependency import get_user, get_admin_user, User, UserRole


def test_get_user_returns_user():
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    user = get_user(x_user_id=user_id, x_user_role=UserRole.USER)

    assert isinstance(user, User)
    assert user.id == str(user_id)
    assert user.role == UserRole.USER


def test_get_admin_user_returns_user_when_admin():
    user = User(id="admin-id", role=UserRole.ADMIN)
    result = get_admin_user(user=user)

    assert result is user


def test_get_admin_user_raises_403_when_not_admin():
    user = User(id="user-id", role=UserRole.USER)

    with pytest.raises(HTTPException) as exc_info:
        get_admin_user(user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Unauthorized"
