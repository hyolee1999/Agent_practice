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
from rag.vector_store import retriever_init, client
from agent.prompt import SYSTEM_PROMPT, ResponseFormat
from agent.llm import generate, stream
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from main import agent_init



def load_chat_page(agent):
    """Load the chat page with the agent and configurations."""

    st.title("Ask Questions About Your PDF")

    

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    query = st.chat_input("Enter your question:")

    if query:
        st.chat_message("user").markdown(query)
        st.session_state.chat_history.append(HumanMessage(content=query))

        with st.chat_message("ai"):
            placeholder = st.empty()
            full_response = ""

            for token in stream(query, agent):
                full_response += token
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.chat_history.append(AIMessage(content=full_response))



if __name__ == "__main__":
    agent  = agent_init()
    load_chat_page(agent)