import streamlit as st
import tempfile
from src.retrieval.retriever import retriever_init, index_pdf_documents
from langchain_openai import OpenAIEmbeddings

dense_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

st.title("Upload PDF to Qdrant")
file = st.file_uploader("Choose a PDF file", type="pdf")


if file is not None:

    with st.spinner("Uploading and indexing PDF..."):
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            pdf_path = tmp.name

        # Index the PDF document
        index_pdf_documents(
            pdf_path=pdf_path,
            _vector_store=qdrant,
            dense_embeddings=dense_embeddings
        )

    st.success("PDF uploaded aÍnd indexed successfully!")