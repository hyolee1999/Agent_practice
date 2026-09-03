"""Application settings and environment configuration."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General App Config
    app_name: str = "DocuAgent AI"
    debug: bool = False

    # LLM API Keys & Models
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, alias="COHERE_API_KEY")

    default_model: str = "anthropic:claude-sonnet-4-6"
    temperature: float = 0.1

    # Qdrant Vector Store
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    collection_name: str = "document_collection"

    # Embedding Models
    dense_embedding_model: str = "BAAI/bge-small-en-v1.5"
    sparse_embedding_model: str = "Qdrant/bm25"

    # RAG Search & Reranking Parameters
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = 200
    top_k: int = Field(default=4, alias="TOP_K")
    rerank_top_n: int = 1
    rerank_model: str = "rerank-english-v3.0"

    # Observability (Langfuse)
    langfuse_public_key: Optional[str] = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_base_url: Optional[str] = Field(default=None, alias="LANGFUSE_BASE_URL")

    # Ollama (Optional)
    ollama_base_url: Optional[str] = Field(default=None, alias="OLLAMA_BASE_URL")
    ollama_api_key: Optional[str] = Field(default=None, alias="OLLAMA_API_KEY")


# Global singleton settings instance
settings = Settings()
