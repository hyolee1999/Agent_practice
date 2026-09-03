"""Streamlit-specific caching layer.

Isolates all @st.cache_resource and @st.cache_data decorators to the presentation layer.
"""

from typing import Optional
import streamlit as st
from docuagent.agent.factory import create_rag_agent
from docuagent.rag.vector_store import get_vector_store


@st.cache_resource(show_spinner="Initializing RAG Agent and Models...")
def get_cached_agent(model_name: Optional[str] = None):
    """Cached initialization of the LangChain RAG agent for Streamlit sessions."""
    return create_rag_agent(model_name=model_name)


@st.cache_resource(show_spinner="Connecting to Vector Store...")
def get_cached_vector_store(collection_name: Optional[str] = None):
    """Cached connection to Qdrant vector store."""
    return get_vector_store(collection_name=collection_name)
