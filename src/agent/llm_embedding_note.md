# LLM Qdrant Embedding Note

## Change Made

- `QdrantVectorStore.from_existing_collection()` now receives a real `OpenAIEmbeddings` instance.
- The previous `embeddings=None` placeholder was removed because `QdrantVectorStore` needs an embedding model for query embedding.
- The unfinished `else:` branch in `qdrant_init()` was replaced with a safe `return None` fallback.

## Result

- Dense retrieval through LangChain can now embed incoming queries correctly.
- The module is no longer left in an incomplete syntax state.