from typing import Self


class IndexCreationException(Exception):
    """Exception raised when index creation fails in the vector database."""
    def __init__(self: Self, msg: str):
        super().__init__(f"Index creation failed in the vector database. Details: {msg}")

class IndexDeletionException(Exception):
    """Exception raised when index deletion fails in the vector database."""
    def __init__(self: Self, msg: str):
        super().__init__(f"Index deletion failed in the vector database. Details: {msg}")

class PutObjectsException(Exception):
    """Exception raised when putting objects into the vector database fails."""
    def __init__(self: Self, msg: str):
        super().__init__(f"Putting objects failed in the vector database. Details: {msg}")

class DeleteObjectsException(Exception):
    """Exception raised when deleting objects from the vector database fails."""
    def __init__(self: Self, msg: str):
        super().__init__(f"Deleting objects failed in the vector database. Details: {msg}")
