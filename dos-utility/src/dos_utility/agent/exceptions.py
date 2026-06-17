from typing import Self


class AgentInitializationException(Exception):
    """Exception raised when an agent provider cannot be initialized."""

    def __init__(self: Self, msg: str):
        super().__init__(f"Agent initialization failed. Details: {msg}")


class ChatGenerationException(Exception):
    """Exception raised when the agent fails to generate a response."""

    def __init__(self: Self, msg: str):
        super().__init__(f"Chat generation failed. Details: {msg}")
