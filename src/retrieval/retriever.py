from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
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



def index_document(client, collection_name, docs: list[Document], sparse_embeddings, dense_embeddings) -> QdrantVectorStore:

    if client.collection_exists(collection_name=collection_name):
        return QdrantVectorStore.from_existing_collection(
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

        return QdrantVectorStore.from_existing_collection(
            client=client,
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retriever_mode= RetrievalMode.HYBRID 
        )








