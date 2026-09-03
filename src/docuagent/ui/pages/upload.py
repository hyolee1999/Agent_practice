"""Streamlit Page: PDF Document Upload and Ingestion."""

import tempfile
from pathlib import Path
import streamlit as st

from docuagent.rag.vector_store import index_pdf_documents

st.title("Upload PDF Documents to Qdrant")
st.markdown("Upload your PDF files below. They will be parsed, split into semantic chunks, and indexed into the Qdrant hybrid vector store.")

with st.form("pdf_upload_form", clear_on_submit=True):
    files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )
    submitted = st.form_submit_button("Index Documents")

if files and submitted:
    total_files = len(files)
    total_chunks = 0
    progress_bar = st.progress(0)

    for idx, file in enumerate(files):
        with st.spinner(f"Indexing '{file.name}'..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = Path(tmp.name)

            try:
                chunks_indexed = index_pdf_documents(tmp_path)
                total_chunks += chunks_indexed
                st.success(f"Indexed **{file.name}** ({chunks_indexed} chunks)")
            except Exception as e:
                st.error(f"Failed to index '{file.name}': {str(e)}")
            finally:
                tmp_path.unlink(missing_ok=True)

        progress_bar.progress((idx + 1) / total_files)

    st.balloons()
    st.info(f"Complete! Indexed a total of {total_chunks} chunks across {total_files} file(s).")
