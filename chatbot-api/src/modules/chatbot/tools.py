from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool, FunctionTool

from src.modules.chatbot.models import get_llm, get_embed_model
from src.modules.chatbot.structured_outputs import (
    PRODUCTS,
    RAGOutput,
    FollowUpQuestionsOutput,
)
from src.modules.settings import SETTINGS


# ---------------------------------------------------------------------------
# Tool names and descriptions
# ---------------------------------------------------------------------------

DEVPORTAL_TOOL_NAME = "DevPortalRAGTool"
CITTADINO_TOOL_NAME = "CittadinoRAGTool"
CHIPS_TOOL_NAME = "FollowUpQuestionsTool"

DEVPORTAL_RAG_TOOL_DESCRIPTION = (
    "RAG tool designed to benefit IT professionals and developers by retrieving "
    "technical, architectural, and integration-related information regarding the "
    f"PagoPA Developer Portal products. "
    f"Use this tool for all technical, architectural, and integration-related queries "
    f"regarding PagoPA Developer Portal products: {PRODUCTS}.\n"
    "Use this tool when the user is an IT professional or a developer seeking to "
    "integrate or manage the PagoPA Developer Portal products.\n"
    "It contains API specifications, authentication methods, SDKs, technical onboarding "
    "for institutions, and backend configuration.\n"
    "DO NOT use this for general 'how to use' questions from citizens."
)

CITTADINO_RAG_TOOL_DESCRIPTION = (
    "RAG tool designed to retrieve information useful for end-users (citizens) with "
    "queries related to the use of Italian digital platforms, specifically those involving "
    "the PagoPA ecosystem. "
    "Use this tool for all queries related to the end-user (citizen) experience of Italian "
    "digital platforms. "
    f"This tool contains comprehensive information on the PagoPA products: {PRODUCTS} "
    "from a user's perspective.\n"
    "Consult this tool for questions about receiving digital notifications, using the App IO "
    "interface, paying taxes or fines as a citizen, troubleshooting payment receipts, and "
    "general help center inquiries (FAQ).\n"
    "DO NOT use this for technical integration or API queries."
)


# ---------------------------------------------------------------------------
# RAG QueryEngineTool
# ---------------------------------------------------------------------------

def get_query_engine_tool(
    index: VectorStoreIndex,
    name: str,
    description: str,
    llm: LLM | None = None,
    embed_model: BaseEmbedding | None = None,
    text_qa_template: PromptTemplate | None = None,
    refine_template: PromptTemplate | None = None,
    verbose: bool = False,
) -> QueryEngineTool:
    """Creates a QueryEngineTool backed by an AutoMergingRetriever.

    Args:
        index: The LlamaIndex VectorStoreIndex to query.
        name: Tool name exposed to the agent.
        description: Tool description used by the agent to decide when to call it.
        llm: Override the default LLM.
        embed_model: Override the default embedding model.
        text_qa_template: Prompt template for question-answering.
        refine_template: Prompt template for answer refinement.
        verbose: Enable verbose logging in the retriever.

    Returns:
        QueryEngineTool ready to be passed to the discovery agent.
    """
    llm = llm or get_llm(temperature=SETTINGS.temperature_rag)
    embed_model = embed_model or get_embed_model()

    base_retriever = index.as_retriever(
        similarity_top_k=SETTINGS.similarity_topk,
        embed_model=embed_model,
    )
    retriever = AutoMergingRetriever(
        base_retriever, index.storage_context, verbose=verbose
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        llm=llm,
        output_cls=RAGOutput,
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        use_async=SETTINGS.use_async,
    )

    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )


# ---------------------------------------------------------------------------
# Follow-up questions (chips) FunctionTool
# ---------------------------------------------------------------------------

async def _generate_questions(
    query_str: str,
    rag_output_devportal: str,
    rag_output_cittadino: str,
) -> FollowUpQuestionsOutput:
    """Generates follow-up questions based on both RAG outputs.

    Use this tool when a user's query is ambiguous and could apply to both
    technical developers (DevPortal) and end-users (CittadinoRAGTool).
    It returns specific questions to help the user choose the right path.
    """
    llm = get_llm()
    sllm = llm.as_structured_llm(output_cls=FollowUpQuestionsOutput)

    prompt = (
        f"Given the user query: {query_str}\n\n"
        f"Given the following context retrieved from the devportal documentation:\n{rag_output_devportal}\n\n"
        f"Given the following context retrieved from the cittadino documentation:\n{rag_output_cittadino}\n\n"
        "Generate a list of questions from the user's perspective (e.g., 'how do I ...', 'how can I ...') "
        "that help them get more detailed information based on the provided context.\n"
        "The questions should be specific and relevant to the information retrieved from both sources, "
        "and should help the user explore topics related to the information already retrieved.\n"
        "Answer: [your answer here (in the same language as the user query)]"
    )

    response = await sllm.acomplete(prompt)
    result = response.raw
    if result is None:
        result = FollowUpQuestionsOutput(questions=[])
    return result


def follow_up_questions_tool(name: str | None = None) -> FunctionTool:
    """Returns a FunctionTool that generates follow-up questions (chips)."""
    return FunctionTool.from_defaults(
        async_fn=_generate_questions,
        name=name or CHIPS_TOOL_NAME,
        description=(
            "Tool to generate follow-up questions for the user.\n"
            "The 'query_str' parameter should contain the original user query.\n"
            "The 'rag_output_devportal' parameter should contain the observations "
            "from the previous DevPortalRAGTool calls.\n"
            "The 'rag_output_cittadino' parameter should contain the observations "
            "from the previous CittadinoRAGTool calls.\n"
            "This helps the user explore topics related to the information already retrieved."
        ),
    )
