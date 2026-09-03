"""Main Streamlit Navigation Entry Point."""

from pathlib import Path
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
PAGES_DIR = CURRENT_DIR / "pages"

st.set_page_config(
    page_title="DocuAgent AI",
    page_icon="🤖",
    layout="wide",
)

upload_page = st.Page(
    str(PAGES_DIR / "upload.py"),
    title="Upload Documents",
    icon="📄",
)

chat_page = st.Page(
    str(PAGES_DIR / "chat.py"),
    title="Chat & Evaluate",
    icon="💬",
)

nav = st.navigation([chat_page, upload_page])
nav.run()
