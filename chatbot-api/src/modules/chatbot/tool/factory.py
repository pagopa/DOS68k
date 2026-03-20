from typing import List, Optional
from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.tools import QueryEngineTool

from ..structured_outputs import RAGOutput


def get_query_engine_tool(
        index: VectorStoreIndex,
        name: str,
        description: str,
        llm: LLM,
        embed_model: BaseEmbedding,
        similarity_top_k: int = 5,
        text_qa_template: Optional[PromptTemplate] = None,
        refine_template: Optional[PromptTemplate] = None,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        use_async: bool = True,
        verbose: bool = False,
    ) -> QueryEngineTool:
    """Builds a QueryEngineTool backed by an AutoMergingRetriever.

    Wraps the given index in an AutoMergingRetriever, feeds it into a
    RetrieverQueryEngine with structured output, and exposes the result
    as a named tool the agent can invoke.

    Args:
        index: The vector store index to retrieve chunks from.
        name: Unique tool name exposed to the agent. Must not contain spaces.
        description: Natural-language description that tells the agent when to use this tool.
        llm: Language model used to synthesise the final answer.
        embed_model: Embedding model used to encode the query at retrieval time.
        similarity_top_k: Number of candidate chunks retrieved before merging. Defaults to 5.
        text_qa_template: Optional prompt template for the initial QA step.
            Must expose {context_str} and {query_str} variables.
        refine_template: Optional prompt template for the answer-refinement step.
            Must expose {existing_answer} and {context_msg} variables.
        node_postprocessors: Optional postprocessors applied after retrieval (e.g. rerankers).
        use_async: Whether to run the query engine in async mode. Defaults to True.
        verbose: Whether to enable verbose logging in the retriever. Defaults to False.

    Returns:
        A QueryEngineTool ready to be registered with a ReActAgent.
    """
    base_retriever: BaseRetriever = index.as_retriever(
        similarity_top_k=similarity_top_k,
        embed_model=embed_model,
    )
    retriever: AutoMergingRetriever = AutoMergingRetriever(
        vector_retriever=base_retriever,
        storage_context=index.storage_context,
        verbose=verbose,
    )
    query_engine: RetrieverQueryEngine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        llm=llm,
        output_cls=RAGOutput,
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        node_postprocessors=node_postprocessors,
        use_async=use_async,
    )

    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )
