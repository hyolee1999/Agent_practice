from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct, VectorParams, SparseVectorParams
from uuid import uuid4
from langchain_core.tools import create_retriever_tool
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



def retriever_init(client, collection_name, sparse_embeddings, dense_embeddings) -> QdrantVectorStore:
    qdrant = None

    if client.collection_exists(collection_name=collection_name):
        qdrant =  QdrantVectorStore.from_existing_collection(
            client=client,
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retriever_mode= RetrievalMode.HYBRID 
        )
    else:
        client.create_collection(
            collection_name = collection_name,
            vectors_config = {
                "dense": models.VectorParams(size=dense_embeddings.dim, distance=models.Distance.COSINE)
            },
            sparse_vectors_config = {
                "sparse": models.SparseVectorParams()
            }
        )

        qdrant =  QdrantVectorStore.from_existing_collection(
            client=client,
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retriever_mode= RetrievalMode.HYBRID 
        )

    retriever = qdrant.as_retriever(search_kwargs={"top_k": 4})

    return create_retriever_tool(retriever, "document_retriever", description = "Search for relevant documents to answer user questions")

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
    






