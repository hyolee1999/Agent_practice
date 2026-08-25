from dataclasses import dataclass

SYSTEM_PROMPT = """You are a document Q&A assistant.
If user asks a question that you do not know, you should refer to the provided tools to answer the question."""


@dataclass
class ResponseFormat():
    summary: str
    chunk_id: str
    page_number: int
    source: str



