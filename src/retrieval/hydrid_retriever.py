# from typing import Any

# from langchain_core.documents import Document
# from langchain_core.retrievers import BaseRetriever
# from pydantic import ConfigDict
# from qdrant_client import models


# def _embed_query(embeddings, query):
#     for method_name in ("query_embeded", "query_embed", "embed_query"):
#         method = getattr(embeddings, method_name, None)
#         if callable(method):
#             return method(query)
#     raise AttributeError("Embedding object does not expose a query embedding method.")


# class HybridRetriever(BaseRetriever):
#     """LangChain-compatible retriever that fuses sparse and dense signals in Qdrant."""

#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     collection_name: str
#     client: Any
#     sparse_embeddings: Any
#     dense_embeddings: Any
#     top_k: int = 4

#     def model_post_init(self, __context: Any) -> None:
#         sparse_model_name = getattr(self.sparse_embeddings, "model_name", None)
#         dense_model_name = getattr(self.dense_embeddings, "model_name", None)

#         if sparse_model_name:
#             self.client.set_sparse_model(sparse_model_name)
#         if dense_model_name:
#             self.client.set_dense_model(dense_model_name)

#     def index_chunks(self, chunks):
#         raise NotImplementedError("Use BM25 or VectorRetriever for indexing.")

#     def search(self, query, top_k=None):
#         """Fuse sparse and dense searches on the same collection."""
#         top_k = top_k or self.top_k
#         bm25_query = _embed_query(self.sparse_embeddings, query)
#         dense_query = _embed_query(self.dense_embeddings, query)

#         try:
#             results = self.client.query_points(
#                 collection_name=self.collection_name,
#                 prefetch=[
#                     models.Prefetch(
#                         query=models.SparseVector(
#                             indices=bm25_query.indices.tolist(),
#                             values=bm25_query.values.tolist(),
#                         ),
#                         using="bm25",
#                         limit=top_k,
#                     ),
#                     models.Prefetch(
#                         query=dense_query,
#                         using="dense",
#                         limit=top_k,
#                     ),
#                 ],
#                 query=models.FusionQuery(fusion=models.Fusion.DBSF),
#                 limit=top_k,
#                 with_payload=True,
#             )
#         except Exception as error:
#             print(f"Error occurred while searching: {error}")
#             return []

#         return [hit.payload.get("text", "") for hit in results.points]

#     def _get_relevant_documents(self, query: str, *, run_manager: Any = None, **kwargs: Any) -> list[Document]:
#         return [Document(page_content=text) for text in self.search(query)]