"""Text chunking strategies: recursive character and semantic chunking."""

from typing import List, Any
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter


def fixed_size_chunker(
    docs: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """Split documents using standard recursive character splitting."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(docs)


def semantic_chunker(
    docs: List[Document],
    embeddings: Any,
) -> List[Document]:
    """Split documents into chunks based on semantic similarity using embeddings."""
    splitter = SemanticChunker(embeddings=embeddings)
    return splitter.split_documents(docs)
