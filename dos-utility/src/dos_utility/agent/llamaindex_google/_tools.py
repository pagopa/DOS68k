from typing import List, Optional

from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool

from ..models import RagToolSpec
from ...vector_db import VectorDBInterface, get_vector_db_instance
from ._structured_outputs import RAGOutput


def _load_index(
    vector_db: VectorDBInterface, embed_model: BaseEmbedding
) -> VectorStoreIndex:
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_db, embed_model=embed_model
    )


def _build_query_engine_tool(
    *,
    index: VectorStoreIndex,
    name: str,
    description: str,
    llm: LLM,
    embed_model: BaseEmbedding,
    similarity_top_k: int,
    text_qa_template: Optional[PromptTemplate],
    refine_template: Optional[PromptTemplate],
    use_async: bool = True,
) -> QueryEngineTool:
    retriever: BaseRetriever = index.as_retriever(
        similarity_top_k=similarity_top_k,
        embed_model=embed_model,
    )
    query_engine: RetrieverQueryEngine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        llm=llm,
        output_cls=RAGOutput,
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        use_async=use_async,
    )

    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )


def build_rag_tools(
    rag_tools: List[RagToolSpec],
    llm: LLM,
    embed_model: BaseEmbedding,
    default_similarity_top_k: int,
) -> List[QueryEngineTool]:
    """Materialise a list of RagToolSpec into LlamaIndex QueryEngineTools.

    Each spec is wired to an index in the configured vector database via
    `dos_utility.vector_db.get_vector_db_instance`.
    """
    tools: List[QueryEngineTool] = []

    for spec in rag_tools:
        qa_template: Optional[PromptTemplate] = (
            PromptTemplate(
                template=spec.qa_prompt,
                template_var_mappings={
                    "context_str": "context_str",
                    "query_str": "query_str",
                },
            )
            if spec.qa_prompt
            else None
        )
        refine_template: Optional[PromptTemplate] = (
            PromptTemplate(
                template=spec.refine_prompt,
                prompt_type="refine",
                template_var_mappings={
                    "existing_answer": "existing_answer",
                    "context_msg": "context_msg",
                },
            )
            if spec.refine_prompt
            else None
        )

        vector_db: VectorDBInterface = get_vector_db_instance(index_name=spec.index_id)
        index: VectorStoreIndex = _load_index(
            vector_db=vector_db, embed_model=embed_model
        )
        tools.append(
            _build_query_engine_tool(
                index=index,
                name=spec.name,
                description=spec.description,
                llm=llm,
                embed_model=embed_model,
                similarity_top_k=spec.similarity_top_k or default_similarity_top_k,
                text_qa_template=qa_template,
                refine_template=refine_template,
            )
        )

    return tools
