"""Qdrant vector store management, hybrid search, and document indexing."""

from functools import lru_cache
from typing import Optional, List, Union
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct

from docuagent.config.settings import settings
from docuagent.ingestion.loader import load_pdf
from docuagent.ingestion.chunker import semantic_chunker
from docuagent.rag.embeddings import dense_embeddings, sparse_embeddings


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Create and return a cached QdrantClient instance."""
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )


def get_vector_store(
    collection_name: Optional[str] = None,
    client: Optional[QdrantClient] = None,
) -> QdrantVectorStore:
    """Initialize or load a hybrid QdrantVectorStore.

    If the collection exists, wraps it directly with dense and sparse vector configurations.
    If not, creates the collection with appropriate dimension and distance metrics.
    """
    col_name = collection_name or settings.collection_name
    q_client = client or get_qdrant_client()

    if q_client.collection_exists(collection_name=col_name):
        return QdrantVectorStore.from_existing_collection(
            collection_name=col_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            validate_collection_config=False,
        )

    # Determine embedding dimension
    _dense_dim = len(dense_embeddings.embed_query("dimension_check"))

    q_client.create_collection(
        collection_name=col_name,
        vectors_config={
            "dense": models.VectorParams(size=_dense_dim, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={"sparse": models.SparseVectorParams()},
    )

    return QdrantVectorStore(
        client=q_client,
        collection_name=col_name,
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name="dense",
        sparse_vector_name="sparse",
    )


def get_retriever(
    collection_name: Optional[str] = None,
    k: Optional[int] = None,
):
    """Return a retriever for the specified vector collection."""
    top_k = k or settings.top_k
    vector_store = get_vector_store(collection_name)
    return vector_store.as_retriever(search_kwargs={"k": top_k})


def index_documents(vector_store: QdrantVectorStore, documents: List[Document]) -> None:
    """Add document chunks to the Qdrant collection."""
    if not documents:
        return
    vector_store.add_documents(documents)


def index_pdf_documents(
    file_path: Union[str, Path],
    collection_name: Optional[str] = None,
) -> int:
    """Load a PDF, generate semantic chunks, and index them into Qdrant.

    Returns:
        int: Number of chunk documents successfully indexed.
    """
    docs = load_pdf(file_path)
    chunks = semantic_chunker(docs, dense_embeddings)
    vstore = get_vector_store(collection_name)
    index_documents(vstore, chunks)
    return len(chunks)
