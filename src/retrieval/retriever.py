from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct, VectorParams, SparseVectorParams
from uuid import uuid4
from langchain_core.tools import create_retriever_tool
# Local ingestion helpers for loading PDFs and semantic chunking
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import semantic_chunker
import streamlit as st

# from abc import ABC, abstractmethod

# class Retriever(ABC):

#     def __init__(self, collection_name, client, embeddings):
#         self.collection_name = collection_name
#         self.client = client
#         self.embeddings = embeddings

#     @abstractmethod
#     def index_chunks(self, chunks):
#         pass
    
#     @abstractmethod
#     def search(self,query, top_k):
#         pass


@st.cache_data(show_spinner=False, persist=True)
def retriever_init(client, collection_name, sparse_embeddings, dense_embeddings) -> QdrantVectorStore:
    """Initialize a QdrantVectorStore backed by the provided client.

    If the collection already exists we wrap it directly; otherwise we create a new
    collection with dense and sparse vector configurations. Explicit ``vector_name``
    and ``sparse_vector_name`` arguments are provided to avoid validation errors when
    re‑using an existing collection.
    """
    qdrant = None

    # When the collection already exists we can simply wrap the existing ``QdrantClient``
    # instance with a ``QdrantVectorStore``. The ``from_existing_collection`` helper
    # expects connection parameters (url, location, …) and does **not** accept a ``client``
    # keyword argument, which caused a ``TypeError``. Instead we instantiate the store
    # directly using the class constructor which does accept a ``client``.
    if client.collection_exists(collection_name=collection_name):
        # The existing collection is expected to have a dense vector named "dense"
        # and a sparse vector named "sparse" (as created below). Explicitly
        # provide these names so that QdrantVectorStore validates correctly.

        qdrant = QdrantVectorStore.from_existing_collection(
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse"        )

    else:
        # Determine the correct size for dense vectors.
        # ``OpenAIEmbeddings`` (and many other LangChain embeddings) may not expose a
        # ``dimensions`` attribute, resulting in ``None`` and causing a ``pydantic``
        # validation error when creating the Qdrant collection.
        # If ``dimensions`` is missing, we fall back to a sensible default that
        # matches the default OpenAI embedding model (text‑embedding‑3‑large → 3072).
        if getattr(dense_embeddings, "dimensions", None) is None:
            _dense_dim: int = 3072
        else:
            _dense_dim = int(dense_embeddings.dimensions)

        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": models.VectorParams(size=_dense_dim, distance=models.Distance.COSINE)
            },
            sparse_vectors_config={"sparse": models.SparseVectorParams()},
        )

        # After creating the collection we instantiate the store directly,
        # specifying the vector names to match the collection configuration.
        qdrant = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

    return qdrant

# # ---------------------------------------------------------------------------
# # Helper: load a PDF, split it into semantic chunks, and index those chunks.
# # ---------------------------------------------------------------------------
# @st.cache_data(show_spinner=False, persist=True)
# def index_pdf_documents(
#     pdf_path: str,
#     _vector_store: QdrantVectorStore,
#     dense_embeddings
# ) -> None:
#     """Load a PDF, create semantic chunks and add them to Qdrant.

#     This function is intended to be called from the Streamlit UI after a user
#     uploads a PDF. It re‑uses the same ``client`` and embedding objects that are
#     used for the retriever, guaranteeing vector‑name consistency.
#     """

#     # 1️⃣ Load the PDF into a list of Document objects.
#     docs: list[Document] = load_pdf(pdf_path)


#     # 2️⃣ Create semantic chunks with the dense embeddings.
#     chunks: list[Document] = semantic_chunker(docs, dense_embeddings)

#     # # 3️⃣ Ensure the Qdrant collection exists (reuse logic from ``retriever_init``).
#     # if client.collection_exists(collection_name=collection_name):
#     #     vector_store = QdrantVectorStore.from_existing_collection(
#     #         collection_name=collection_name,
#     #         embedding=dense_embeddings,
#     #         sparse_embedding=sparse_embeddings,
#     #         retrieval_mode=RetrievalMode.HYBRID,
#     #         vector_name="dense",
#     #         sparse_vector_name="sparse",
#     #         validate_collection_config=False,
#     #     )
#     # else:
#     #     dense_dim = getattr(dense_embeddings, "dimensions", None) or 3072
#     #     client.create_collection(
#     #         collection_name=collection_name,
#     #         vectors_config={"dense": models.VectorParams(size=int(dense_dim), distance=models.Distance.COSINE)},
#     #         sparse_vectors_config={"sparse": models.SparseVectorParams()},
#     #     )
#     #     vector_store = QdrantVectorStore(
#     #         client=client,
#     #         collection_name=collection_name,
#     #         embedding=dense_embeddings,
#     #         sparse_embedding=sparse_embeddings,
#     #         retrieval_mode=RetrievalMode.HYBRID,
#     #         vector_name="dense",
#     #         sparse_vector_name="sparse",
#     #     )

#     # 4️⃣ Index the semantic chunks.
#     index_documents(_vector_store, chunks)

def index_documents(vector_store: QdrantVectorStore, documents: list[Document]):
    """Index documents into the Qdrant collection."""
    try:
        vector_store.add_documents(documents)
    except Exception as error:
        print(f"Error occurred while indexing documents: {error}")


def index_points(client: QdrantClient, collection_name, dense_vectors: list[dict], sparse_vectors: list[dict]):
    """Index points into the Qdrant collection."""

    hybrid_points = PointStruct(
        id= str(uuid4()),
        vector = {
            "dense": dense_vectors,
            "sparse": sparse_vectors
        }
    )
    try:
        client.upsert(
            collection_name=collection_name,
            points=hybrid_points)
    except Exception as error:
        print(f"Error occurred while indexing points: {error}")
    






