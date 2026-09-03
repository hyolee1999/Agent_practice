"""Tool definitions for the agent."""

from typing import Optional
from langchain_core.tools import BaseTool, create_retriever_tool
from langchain_cohere import CohereRerank
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever

from docuagent.config.settings import settings
from docuagent.rag.vector_store import get_retriever


def create_document_retriever_tool(
    collection_name: Optional[str] = None,
    tool_name: str = "document_retriever",
    description: str = "Search for relevant documents to answer user questions",
) -> BaseTool:
    """Create a contextual compression retriever tool backed by Qdrant and Cohere reranking."""
    base_retriever = get_retriever(collection_name=collection_name, k=settings.top_k)

    if settings.cohere_api_key:
        compressor = CohereRerank(
            model=settings.rerank_model,
            top_n=settings.rerank_top_n,
            cohere_api_key=settings.cohere_api_key,
        )
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever,
        )
    else:
        retriever = base_retriever

    return create_retriever_tool(
        retriever,
        tool_name,
        description=description,
    )
