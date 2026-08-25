# from qdrant_client.models import SparseVector

# from src.retrieval.retriever import Retriever


# class BM25(Retriever):
#     def __init__(self, collection_name, client, embeddings, sparse_embeddings=None):
#         super().__init__(collection_name, client, embeddings)
#         self.sparse_embeddings = sparse_embeddings or embeddings
#         model_name = getattr(self.sparse_embeddings, "model_name", None) or "Qdrant/bm25"
#         self.client.set_sparse_model(model_name)

#     def index_chunks(self, chunks):
#         """Index chunks into the shared sparse/BM25-backed collection."""
#         try:
#             self.client.add(
#                 collection_name=self.collection_name,
#                 documents=[chunk.page_content for chunk in chunks],
#             )
#         except Exception as error:
#             print(f"Error occurred while indexing chunks: {error}")

#     def _embed_sparse_query(self, query):
#         for method_name in ("query_embeded", "query_embed", "embed_query"):
#             method = getattr(self.sparse_embeddings, method_name, None)
#             if callable(method):
#                 return method(query)
#         raise AttributeError("Sparse embeddings object does not expose a query embedding method.")

#     def search(self, query, top_k) -> list:
#         """Search the sparse index with the configured sparse embedding model."""
#         bm25_query = self._embed_sparse_query(query)

#         try:
#             bm25_hits = self.client.query_points(
#                 collection_name=self.collection_name,
#                 query=SparseVector(
#                     indices=bm25_query.indices.tolist(),
#                     values=bm25_query.values.tolist(),
#                 ),
#                 limit=top_k,
#                 with_payload=True,
#             )
#         except Exception as error:
#             print(f"Error occurred while searching: {error}")
#             return []

#         return [hit.payload.get("text", "") for hit in bm25_hits.points]