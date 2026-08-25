from dataclasses import dataclass

SYSTEM_PROMPT = """You are a document Q&A assistant.
Answer ONLY using the context provided below.
For each claim, cite the chunk ID in [brackets].
If the context does not contain the answer, say:
'I cannot find this in the provided documents.'
Never fabricate information."""


@dataclass
class ResponseFormat():
    summary: str
    chunk_id: str
    page_number: int
    source: str



