import streamlit as st
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.tools import create_retriever_tool
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain_qdrant import FastEmbedSparse
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient, models
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from ingestion.ingestion_manager import raw_to_documents
from langchain_core.documents import Document
from dotenv import load_dotenv
from retrieval.retriever import retriever_init, index_pdf_documents
from generate.prompt import SYSTEM_PROMPT, ResponseFormat
from generate.llm import generate, stream
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

def env_init():
    """Initialize environment variables and configurations."""
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
    dense_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    model = init_chat_model(model="gpt-5.5", temperature=0.1)
    checkpointer = InMemorySaver()

    config = {'configurable': {'thread_id': str(uuid4())}}

    # Create a single Qdrant client that will be reused for both retrieval and indexing.
    qdrant_client = QdrantClient(url="http://localhost:6333")

    qdrant = retriever_init(
        client=qdrant_client,
        collection_name="document_collection",
        sparse_embeddings=sparse_embeddings,
        dense_embeddings=dense_embeddings,
    )

    retriever = qdrant.as_retriever(search_kwargs={"k": 1})

    retriever_tool = create_retriever_tool(
        retriever,
        "document_retriever",
        description="Search for relevant documents to answer user questions",
    )

    agent = create_agent(
        model=model,
        tools=[retriever_tool],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

    return agent, config, qdrant


@st.fragment
def load_chat_page(agent, config):
    """Load the chat page with the agent and configurations."""

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    st.title("Ask Questions About Your PDF")
    query = st.text_input("Enter your question:")

    if query:
        st.chat_message("user").markdown(query)
        st.session_state.chat_history.append(HumanMessage(content=query))

        with st.chat_message("ai"):
            placeholder = st.empty()
            full_response = ""

            for token in stream(query, agent, config):
                full_response += token
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.chat_history.append(AIMessage(content=full_response))



if __name__ == "__main__":
    agent, config, qdrant = env_init()
    load_chat_page(agent, config)