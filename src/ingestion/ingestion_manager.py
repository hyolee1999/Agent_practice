# Import all public functions from the sibling modules.
from .chunker import semantic_chunker, fix_chunk  # noqa: F403,F401
from .pdf_loader import load_pdf  # noqa: F403,F401


def raw_to_documents(file_path: str, embedding) -> list[dict]:
    """
    Converts raw data into a list of document dictionaries.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of document dictionaries, where each dictionary contains 'page_number' and 'text'.
    """
    page_list = load_pdf(file_path)

    chunks = semantic_chunker(page_list, embedding)

    return chunks



    



