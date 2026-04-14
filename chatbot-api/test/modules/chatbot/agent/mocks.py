from typing import Self
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.agent.react.formatter import ReActChatFormatter

class ReActAgentMock(ReActAgent):
    def __new__(cls, **kwargs):
        # ReActAgent is a Pydantic v2 BaseModel. Calling super().__init__() would
        # trigger real agent initialisation, while model_construct() causes infinite
        # recursion because it internally calls cls.__new__(cls).
        # Instead, we allocate the instance with object.__new__ and manually seed
        # the two Pydantic internals (__pydantic_fields_set__, __pydantic_extra__)
        # that __getattr__/__setattr__ depend on, then set formatter so that
        # get_agent() can write agent.formatter.system_header without errors.
        instance = object.__new__(cls)
        object.__setattr__(instance, "__pydantic_fields_set__", set())
        object.__setattr__(instance, "__pydantic_extra__", None)
        object.__setattr__(instance, "formatter", ReActChatFormatter())
        return instance

    def __init__(self: Self, **kwargs):
        pass
