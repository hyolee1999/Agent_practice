# Retrieval Optimization Summary

## What Changed

- `BM25` now focuses on sparse indexing and sparse retrieval against the shared Qdrant client.
- `VectorRetriever` now exists as a real class, so dense indexing and dense retrieval are supported directly.
- `HybridRetriever` is now a LangChain `BaseRetriever`, so it can be passed into chains and RAG pipelines that expect `invoke()` / `get_relevant_documents()` behavior.
- `HybridRetriever` still fuses sparse and dense searches against the shared Qdrant client instead of handling indexing.
- The broken `openai.models` import and the duplicate `models` import in the hybrid retriever were removed.
- Backward-compatible function wrappers remain in `vector_store.py` so existing imports can keep working.

## Behavior

- Sparse indexing uses the BM25 client path.
- Dense indexing uses point upserts with dense embeddings.
- Hybrid querying uses a single shared client with sparse and dense prefetches fused by Qdrant.

## Notes

- `HybridRetriever` is query-only and LangChain-compatible; use `BM25` or `VectorRetriever` for indexing.
- All retrievers still share the same client instance, so collection configuration stays centralized.