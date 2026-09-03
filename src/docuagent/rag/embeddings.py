"""Embedding models configuration (Dense and Sparse embeddings)."""

from functools import lru_cache
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse

from docuagent.config.settings import settings
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_sparse_embeddings() -> FastEmbedSparse:
    """Instantiate or return cached Sparse BM25 embeddings."""
    return FastEmbedSparse(model_name=settings.sparse_embedding_model)


@lru_cache(maxsize=1)
def get_dense_embeddings() -> FastEmbedEmbeddings:
    """Instantiate or return cached Dense embeddings."""
    return FastEmbedEmbeddings(model_name=settings.dense_embedding_model)


# Module-level singletons for convenience
sparse_embeddings = get_sparse_embeddings()
dense_embeddings = get_dense_embeddings()
