"""System prompts and prompt templates for the agent."""

from dataclasses import dataclass

SYSTEM_PROMPT = """You are a professional document Q&A assistant.
If the user asks a question, always refer to the provided document retriever tool to find grounded information.
Be clear, accurate, and concise. Do not fabricate facts that are not present in the retrieved documents."""


@dataclass
class ResponseFormat:
    """Structured response format metadata."""
    summary: str
    chunk_id: str
    page_number: int
    source: str
