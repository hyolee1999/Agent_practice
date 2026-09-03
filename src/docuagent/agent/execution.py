"""Execution helpers for running agents synchronously, streaming, and asynchronously."""

from typing import Generator, AsyncGenerator, Optional, Dict, Any
from langchain_core.messages import AIMessageChunk

from docuagent.observability.langfuse import get_agent_config


def generate(query: str, agent: Any, config: Optional[Dict[str, Any]] = None) -> str:
    """Execute a single-turn query with the agent synchronously and return final response."""
    cfg = config or get_agent_config()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=cfg,
    )
    return result["messages"][-1].content


def stream(query: str, agent: Any, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
    """Stream token deltas synchronously from the agent."""
    cfg = config or get_agent_config()

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        config=cfg,
        stream_mode="messages",
        version="v2",
    ):
        if chunk.get("type") == "messages":
            token, _ = chunk["data"]
            if getattr(token, "content_blocks", None) and isinstance(token, AIMessageChunk):
                block = token.content_blocks[0]
                if isinstance(block, dict) and "text" in block:
                    yield block["text"]
            elif getattr(token, "content", None):
                yield token.content


async def astream(query: str, agent: Any, config: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
    """Stream tokens asynchronously for FastAPI SSE endpoints."""
    cfg = config or get_agent_config()

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": query}]},
        config=cfg,
        stream_mode="messages",
    ):
        if isinstance(chunk, tuple):
            message, _ = chunk
            content = getattr(message, "content", "")
            if content:
                yield content
        elif isinstance(chunk, dict) and "messages" in chunk:
            msg = chunk["messages"][-1]
            content = getattr(msg, "content", "")
            if content:
                yield content
