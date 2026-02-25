from fastapi import HTTPException, status


def get_session_service_get_sessions_mock():
    class SessionServiceMock:
        async def get_sessions(self, user_id: str):
            return [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": user_id,
                    "title": "Session 1",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "user_id": user_id,
                    "title": "Session 2",
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
                },
            ]

    return SessionServiceMock()

def get_session_service_get_session_200_mock():
    class SessionServiceMock:
        async def get_session(self, session_id: str, user_id: str):
            return {
                "id": session_id,
                "user_id": user_id,
                "title": "Session 1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
            }

    return SessionServiceMock()

def get_session_service_get_session_404_mock():
    class SessionServiceMock:
        async def get_session(self, session_id: str, user_id: str):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionServiceMock()

def get_session_service_create_session_mock():
    class SessionServiceMock:
        async def create_session(self, user_id: str, session_data: dict, is_temporary: bool):
            return {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": user_id,
                "title": session_data["title"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "expires_at": "2024-01-02T00:00:00Z",
            }

    return SessionServiceMock()

def get_session_service_delete_session_204_mock():
    class SessionServiceMock:
        async def delete_session(self, session_id: str, user_id: str):
            return

    return SessionServiceMock()

def get_session_service_delete_session_404_mock():
    class SessionServiceMock:
        async def delete_session(self, session_id: str, user_id: str):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionServiceMock()