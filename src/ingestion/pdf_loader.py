from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
# import fitz

# def load_pdf(file_bytes) -> list[dict]:
#     """
#     Loads a PDF from a byte stream and extracts its text content.

#     Args:
#         file_bytes (bytes): The raw bytes of the PDF file.

#     Returns:
#         list[dict]: A list of dictionaries, each containing ``page_number`` and ``text`` keys.
#     """

#     try:
#         doc = fitz.open(stream=file_bytes, filetype="pdf")
#     except Exception as e:
#         print(f"Error occurred while opening the PDF file: {e}")
#         return []

#     chunks = []
#     for idx, page in enumerate(doc, start=1):
#         text = page.get_text("text")
#         chunks.append({"page_number": idx, "text": text})

#     doc.close()
#     return chunks

def load_pdf(file_path) -> list[Document]:
    """
    Loads a PDF from a file path and extracts its text content.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list[Document]: A list of Document objects, each containing the text content of a page.
    """
    loader = PyMuPDFLoader(file_path)
    return loader.load()



