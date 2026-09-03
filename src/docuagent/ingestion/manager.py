"""Ingestion orchestration pipeline: file -> loaded documents -> chunks."""

from pathlib import Path
from typing import List, Union, Any, Optional
from langchain_core.documents import Document

from docuagent.ingestion.loader import load_pdf
from docuagent.ingestion.chunker import semantic_chunker, fixed_size_chunker


def process_pdf_to_documents(
    file_path: Union[str, Path],
    embedding_model: Optional[Any] = None,
    use_semantic: bool = True,
) -> List[Document]:
    """Load a PDF and convert it into indexed chunk Documents.

    Args:
        file_path: Absolute or relative path to PDF file.
        embedding_model: Embedding instance for semantic splitting.
        use_semantic: If True and embedding_model provided, uses semantic chunker.
                      Otherwise falls back to fixed size chunker.

    Returns:
        List[Document]: Chunked documents ready for vector store indexing.
    """
    raw_pages = load_pdf(file_path)

    if use_semantic and embedding_model is not None:
        return semantic_chunker(raw_pages, embeddings=embedding_model)
    return fixed_size_chunker(raw_pages)
