"""DocuAgent AI Package.

A modular, production-ready Document RAG Agent with Hybrid Search,
Observability (Langfuse + Ragas), and multi-interface delivery (FastAPI + Streamlit).
"""

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# Compatibility Shim for Ragas Issue #2745 (Broken ChatVertexAI / VertexAI imports)
# In langchain-community >= 0.4, VertexAI classes moved to langchain-google-vertexai.
# Unpatched Ragas on PyPI (e.g. Streamlit Cloud) imports from the old paths.
# We map the old paths in sys.modules to langchain_google_vertexai at runtime.
# ---------------------------------------------------------------------------
import sys

if "langchain_community.chat_models.vertexai" not in sys.modules:
    try:
        import langchain_google_vertexai

        sys.modules["langchain_community.chat_models.vertexai"] = langchain_google_vertexai
        sys.modules["langchain_community.llms.vertexai"] = langchain_google_vertexai
        try:
            import langchain_community.llms

            langchain_community.llms.VertexAI = langchain_google_vertexai.VertexAI
        except (ImportError, AttributeError):
            pass
    except ImportError:
        pass
