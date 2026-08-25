# from qdrant_client.models import PointStruct

# from src.retrieval.retriever import Retriever


# def _embed_dense(embeddings, text):
#     for method_name in ("embed_query", "query_embeded", "query_embed"):
#         method = getattr(embeddings, method_name, None)
#         if callable(method):
#             return method(text)
#     raise AttributeError("Dense embeddings object does not expose a query embedding method.")


# class VectorRetriever(Retriever):
#     def __init__(self, collection_name, client, embeddings):
#         super().__init__(collection_name, client, embeddings)
#         model_name = getattr(self.embeddings, "model_name", None)
#         if model_name:
#             self.client.set_dense_model(model_name)

#     def index_chunks(self, chunks):
#         """Index chunks as dense vectors in the shared Qdrant client."""
#         points = []
#         for index, chunk in enumerate(chunks):
#             vector = _embed_dense(self.embeddings, chunk.page_content)
#             points.append(
#                 PointStruct(
#                     id=str(index),
#                     vector=vector,
#                     payload={"text": chunk.page_content},
#                 )
#             )

#         try:
#             self.client.upsert_points(collection_name=self.collection_name, points=points)
#         except Exception as error:
#             print(f"Error occurred while indexing chunks: {error}")

#     def search(self, query, top_k) -> list:
#         """Search the dense vector index with the configured embedding model."""
#         query_vector = _embed_dense(self.embeddings, query)

#         try:
#             hits = self.client.query_points(
#                 collection_name=self.collection_name,
#                 query=query_vector,
#                 limit=top_k,
#                 with_payload=True,
#             )
#         except Exception as error:
#             print(f"Error occurred while searching: {error}")
#             return []

#         return [hit.payload.get("text", "") for hit in hits.points]


# def index_chunks(chunks, collection_name, client, embeddings):
#     """Backward-compatible helper for dense indexing."""
#     return VectorRetriever(collection_name, client, embeddings).index_chunks(chunks)


# def search(query, client, collection_name, embeddings, top_k) -> list:
#     """Backward-compatible helper for dense search."""
#     return VectorRetriever(collection_name, client, embeddings).search(query, top_k)