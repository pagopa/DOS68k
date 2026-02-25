from fastapi import Header
from typing import Optional, Annotated

def get_user_id(x_user_id: Annotated[Optional[str], Header()] = None) -> str:
    return "123e4567-e89b-12d3-a456-426614174000" #! Change