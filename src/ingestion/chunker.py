from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# def fix_chunk(pages, chunk_size=1000, chunk_overlap=200):
#     """
#     Splits the given pages into smaller chunks based on the specified chunk size and overlap.

#     Args:
#         pages (list): A list of page content strings to be chunked.
#         chunk_size (int): The maximum size of each chunk.
#         chunk_overlap (int): The number of overlapping characters between consecutive chunks.

#     Returns:
#         list: A list of chunked content strings.
#     """
#     chunks = []
#     for page in pages:
#         for i in range(0, len(page), chunk_size - chunk_overlap):
#             chunks.append(page[i:i + chunk_size])
#     return chunks


# def semantic_chunks(pages, embeddings, chunk_size=1000, chunk_overlap=200):
#     """
#     Splits the given pages into smaller chunks based on semantic similarity using embeddings.

#     Args:
#         pages (list): A list of page content strings to be chunked.
#         embeddings (Embeddings): An instance of the Embeddings class for generating vector embeddings.
#         chunk_size (int): The maximum size of each chunk.
#         chunk_overlap (int): The number of overlapping characters between consecutive chunks.

#     Returns:
#         list: A list of semantically chunked content strings.
#     """
#     chunks = []
#     for page in pages:
#         page_chunks = fix_chunk([page], chunk_size, chunk_overlap)
#         for chunk in page_chunks:
#             vector = embeddings.embed_query(chunk)
#             chunks.append({"text": chunk, "vector": vector})
#     return chunks



def fix_chunk(docs: list[Document]) -> list[Document]:
    """
    Splits the given documents into smaller chunks based on the specified chunk size and overlap.

    Args:
        docs (list[Document]): A list of Document objects to be chunked.

    Returns:
        RecursiveCharacterTextSplitter: A text splitter instance.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)
    return chunks



def semantic_chunker(docs: list[Document], embeddings) -> list[Document]:
    """
    Splits the given documents into smaller chunks based on semantic similarity using embeddings.

    Args:
        docs (list[Document]): A list of Document objects to be chunked.
        embeddings (Embeddings): An instance of the Embeddings class for generating vector embeddings.

    Returns:
        list[Document]: A list of Document objects representing the semantically chunked content.
    """

    splitter = SemanticChunker(embeddings=embeddings)

    chunks = splitter.split_documents(docs)

    return chunks
