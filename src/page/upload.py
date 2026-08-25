import streamlit as st
import tempfile
from rag.vector_store import index_pdf_documents


st.title("Upload PDF to Qdrant")

with st.form("pdf_upload", clear_on_submit=True):

    files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    submitted = st.form_submit_button("Submit")


if files and submitted:

    with st.spinner("Uploading and indexing PDF..."):
        # Save the uploaded file to a temporary location
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                pdf_path = tmp.name

            index_pdf_documents(pdf_path)
            st.success(f"PDF '{file.name}' uploaded and indexed successfully!")
    