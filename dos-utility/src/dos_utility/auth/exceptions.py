from typing import Self, Optional


class EmptyTokenException(Exception):
    def __init__(self: Self):
        super().__init__("Invalid empty token")

class InvalidTokenKeyException(Exception):
    def __init__(self: Self, msg: Optional[str]=None):
        super().__init__("Invalid token key" if msg is None else msg)

class InvalidTokenException(Exception):
    def __init__(self: Self, msg: Optional[str]=None):
        super().__init__("Invalid token" if msg is None else msg)

class TokenExpiredException(Exception):
    def __init__(self: Self):
        super().__init__("Token expired")