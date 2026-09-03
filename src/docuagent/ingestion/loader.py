"""Document loaders for raw file formats (PDF, text, etc.)."""

from pathlib import Path
from typing import Union
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document


def load_pdf(file_path: Union[str, Path]) -> list[Document]:
    """Load a PDF from file path and extract page-by-page documents.

    Args:
        file_path: Path to the PDF file.

    Returns:
        list[Document]: LangChain Document objects containing text and metadata per page.
    """
    path_str = str(file_path)
    loader = PyMuPDFLoader(path_str)
    return loader.load()
