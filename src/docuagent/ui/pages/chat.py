"""Streamlit Page: Interactive Q&A Chat with Ragas Evaluation & Langfuse Tracing."""

import asyncio
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from docuagent.ui.cache import get_cached_agent
from docuagent.agent.execution import generate
from docuagent.observability.langfuse import get_agent_config
from docuagent.observability.metrics import eval_trace

st.title("Ask Questions About Your Documents")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Render past messages
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# User input query
query = st.chat_input("Enter your question:")

if query:
    # Render user prompt
    st.chat_message("user").markdown(query)
    st.session_state.chat_history.append(HumanMessage(content=query))

    # Retrieve agent
    agent = get_cached_agent()
    config = get_agent_config()

    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Generating answer and querying vector store..."):
            full_response = generate(query, agent, config=config)
            placeholder.markdown(full_response)

        # Run Ragas evaluation in background and log to Langfuse
        with st.status("Evaluating response with Ragas...", expanded=False) as status:
            try:
                scores = asyncio.run(eval_trace(question=query, answer=full_response))
                st.write("**Evaluation Metrics:**")
                cols = st.columns(len(scores))
                for idx, (metric_name, val) in enumerate(scores.items()):
                    cols[idx].metric(label=metric_name, value=f"{val:.2f}")
                status.update(label="Evaluation logged to Langfuse!", state="complete")
            except Exception as eval_err:
                status.update(label=f"Evaluation note: {str(eval_err)}", state="error")

        st.session_state.chat_history.append(AIMessage(content=full_response))
