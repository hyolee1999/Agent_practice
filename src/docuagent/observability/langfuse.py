"""Langfuse tracing, callback handlers, and tool call interceptor middleware."""

from typing import List, Optional, Dict, Any
from functools import lru_cache
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest

from docuagent.config.settings import settings


class ContextManager:
    """Thread-safe context store for collecting retrieved documents from tool calls."""

    def __init__(self):
        self._contexts: List[str] = []

    def add(self, text: str) -> None:
        self._contexts.append(text)

    def get_all(self) -> List[str]:
        return list(self._contexts)

    def clear(self) -> None:
        self._contexts.clear()


# Global context manager instance
context_manager = ContextManager()


@lru_cache(maxsize=1)
def get_langfuse_client():
    """Return cached Langfuse client."""
    return get_client()


@lru_cache(maxsize=1)
def get_langfuse_callback() -> CallbackHandler:
    """Return cached Langfuse CallbackHandler for LangChain / LangGraph."""
    return CallbackHandler()


def get_agent_config(thread_id: str = "1") -> Dict[str, Any]:
    """Return LangChain/LangGraph execution config with Langfuse callback."""
    return {
        "configurable": {"thread_id": thread_id},
        "callbacks": [get_langfuse_callback()],
    }


@wrap_tool_call
def intercept_retriever(request: ToolCallRequest, handler):
    """LangChain middleware to intercept retriever tool calls and capture context."""
    result = handler(request)

    if request.tool_call.get("name") == "document_retriever":
        content = getattr(result, "content", str(result))
        context_manager.add(content)

    return result
