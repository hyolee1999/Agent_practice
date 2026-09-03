"""Streamlit main entry point shim.

Points to the modularized docuagent.ui.pages.
"""

from pathlib import Path
import streamlit as st

PAGES_DIR = Path(__file__).resolve().parent / "docuagent" / "ui" / "pages"

upload_page = st.Page(str(PAGES_DIR / "upload.py"), title="Import PDF to Qdrant", icon="📄")
chat_page = st.Page(str(PAGES_DIR / "chat.py"), title="Ask question", icon="💬")

page = st.navigation([upload_page, chat_page])
page.run()