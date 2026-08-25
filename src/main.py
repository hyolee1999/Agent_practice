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


load_dotenv()
     

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
dense_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

model = init_chat_model(model="openai:gpt-5.5", temperature=0.1)

checkpointer = InMemorySaver()

config = {'configurable': {'thread_id': 1}}

# Create a single Qdrant client that will be reused for both retrieval and indexing.
qdrant_client = QdrantClient(url="http://localhost:6333")

retriever_tool = retriever_init(
    client=qdrant_client,
    collection_name="document_collection",
    sparse_embeddings=sparse_embeddings,
    dense_embeddings=dense_embeddings,
)

# vector_retriever = vector_store.as_retriever(search_kwargs={"top_k": 4})

# retriever_tool = create_retriever_tool(vector_retriever, "document_retriever", description = "Search for relevant documents to answer user questions")

agent = create_agent(
    model=model,
    tools=[retriever_tool],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
    response_format=ResponseFormat
)


st.title("PDF Chat")
uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

if uploaded_file is not None:

    # file_bytes = uploaded_file.read()

    # pages = raw_to_documents(file_bytes)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.session_state["pdf_path"] = pdf_path
    st.success(f"Selected: {pdf_path}")
    st.write(pdf_path)

    # ------------------------------------------------------------
    # 5️⃣  Index the PDF – load, chunk semantically, and store.
    # ------------------------------------------------------------
    with st.spinner("Indexing PDF…"):
        index_pdf_documents(
            pdf_path=pdf_path,
            client=qdrant_client,
            collection_name="document_collection",
            sparse_embeddings=sparse_embeddings,
            dense_embeddings=dense_embeddings,
        )

    user_query = st.chat_input("Ask a question about the uploaded PDF")
    if user_query:
        st.chat_message("user").write(user_query)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            # for token in stream(user_query, agent, config):
            #     full_response += token
            #     placeholder.markdown(full_response + "▌")

            full_response = generate(user_query, agent, config)


            print("Test Test Test")
            print("Response: ", full_response)
            placeholder.markdown(full_response)
        # st.chat_message("assistant").write("I will answer this after connecting your retriever.")
