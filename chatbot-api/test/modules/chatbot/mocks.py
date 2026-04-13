from typing import Self
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding


class GoogleGenAIMock(GoogleGenAI):
    def __init__(self: Self, **kwargs):
        pass

class GoogleGenAIEmbeddingMock(GoogleGenAIEmbedding):
    def __init__(self: Self, **kwargs):
        pass
