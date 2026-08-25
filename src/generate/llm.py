from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.tools import create_retriever_tool
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient, models
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from ingestion.ingestion_manager import raw_to_documents
from langchain_core.documents import Document
# import streamlit as st
# import tempfile
# from pathlib import Path






def qdrant_init(client,collection_name, dense_embeddings, sparse_embeddings):
    # client = QdrantClient(url="http://localhost:6333")
    

    if client.collection_exists(collection_name=collection_name):
        return QdrantVectorStore.from_existing_collection(
            client=client,
            collection_name=collection_name,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            retriever_mode="hybrid"
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
            retriever_mode="hybrid"
        )


def generate(query: str, chunk:list[Document] ) -> str:
    """Generate an answer to the query using the agent."""




    return None


def stream(query: str, chunk:list[Document], callback: ToolRuntime) -> str:
    """Stream the answer to the query using the agent."""

    return None



if __name__ == "__main__":
    # load_dotenv()

    # SYSTEM_PROMPT = """You are a document Q&A assistant.
    # Answer ONLY using the context provided below.
    # For each claim, cite the chunk ID in [brackets].
    # If the context does not contain the answer, say:
    # 'I cannot find this in the provided documents.'
    # Never fabricate information."""

    # sparse_embeddings = SparseTextEmbedding(model_name="Qdrant/bm25")
    # dense_embeddings = OpenAIEmbeddings(model_name="text-embedding-3-large")

    # model = init_chat_model(model_name="gpt-4o", temperature=0.1)

    # checkpointer = InMemorySaver()

    # config = {'configuration': {'thread_id': 1}}

    # vector_store = qdrant_init()

    # vector_retriever = vector_store.as_retriever(search_kwargs={"top_k": 4})

    # retriever_tool = create_retriever_tool(vector_retriever, "document_retriever", description = "Search for relevant documents to answer user questions")

    # agent = create_agent(
    #     model=model,
    #     tools=[retriever_tool],
    #     system_message=SYSTEM_PROMPT,
    #     checkpointer=checkpointer,
    #     verbose=True,
    # )
    














    










    