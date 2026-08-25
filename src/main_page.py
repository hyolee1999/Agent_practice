import streamlit as st

upload_page = st.Page("page/upload.py",title = "Import PDF to Qdrant", icon="📄")

chat_page = st.Page("page/chat.py", title="Ask question", icon="💬")

page = st.navigation([upload_page, chat_page])

page.run()