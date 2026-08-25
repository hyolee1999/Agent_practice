import streamlit as st
import tempfile
from src.rag.vector_store import index_pdf_documents


st.title("Upload PDF to Qdrant")
file = st.file_uploader("Choose a PDF file", type="pdf")



if file is not None:

    with st.spinner("Uploading and indexing PDF..."):
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            pdf_path = tmp.name

        # qdrant = retriever_init(
        #     collection_name="document_collection"
        # )

        index_pdf_documents(pdf_path)

    st.success("PDF uploaded and indexed successfully!")