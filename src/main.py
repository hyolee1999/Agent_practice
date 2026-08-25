import streamlit as st
import tempfile
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.tools import create_retriever_tool
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from rag.embeddings import sparse_embeddings, dense_embeddings
from qdrant_client import QdrantClient, models
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from langchain_core.documents import Document
from dotenv import load_dotenv
from rag.vector_store import retriever_init, index_pdf_documents, client
from agent.prompt import SYSTEM_PROMPT, ResponseFormat
from agent.llm import generate, stream
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from langchain_cohere import CohereRerank
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever


load_dotenv()

@st.cache_resource()
def agent_init():

    model = init_chat_model(model="deepseek-chat", temperature=0.1)
    checkpointer = InMemorySaver()

    # config = {'configurable': {'thread_id': str(uuid4())}}

    qdrant = retriever_init(
        collection_name="document_collection"
    )

    retriever = qdrant.as_retriever(search_kwargs={"k": 4})

    compressor =  CohereRerank(model="rerank-english-v3.0", top_n = 1)

    compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

    retriever_tool = create_retriever_tool(
        compression_retriever,
        "document_retriever",
        description="Search for relevant documents to answer user questions",
    )


    agent = create_agent(
        model=model,
        tools=[retriever_tool],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )
    return agent

# st.title("PDF Chat")
# uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

# if uploaded_file is not None:

#     # file_bytes = uploaded_file.read()

#     # pages = raw_to_documents(file_bytes)

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(uploaded_file.read())
#         pdf_path = tmp.name

#     st.session_state["pdf_path"] = pdf_path
#     st.success(f"Selected: {pdf_path}")
#     st.write(pdf_path)

#     # ------------------------------------------------------------
#     # 5️⃣  Index the PDF – load, chunk semantically, and store.
#     # ------------------------------------------------------------
#     with st.spinner("Indexing PDF…"):
#         index_pdf_documents(
#             pdf_path=pdf_path
#         )
#         print("PDF indexed successfully.")

#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     for message in st.session_state.chat_history:
#         if isinstance(message, HumanMessage):
#             with st.chat_message("user"):
#                 st.markdown(message.content)
#         elif isinstance(message, AIMessage):
#             with st.chat_message("assistant"):
#                 st.markdown(message.content)

#     user_query = st.chat_input("Ask a question about the uploaded PDF")
#     if user_query:
#         st.chat_message("user").write(user_query)
#         st.session_state.chat_history.append(HumanMessage(content=user_query))

#         with st.chat_message("assistant"):
#             placeholder = st.empty()
#             full_response = ""

#             for token in stream(user_query, agent_init()):
#                 full_response += token
#                 placeholder.markdown(full_response + "▌")

#             placeholder.markdown(full_response)
#             st.session_state.chat_history.append(AIMessage(content=full_response))


