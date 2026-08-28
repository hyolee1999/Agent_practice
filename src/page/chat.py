import streamlit as st
from agent.llm import generate
from langchain_core.messages import HumanMessage, AIMessage
from main import agent_init, eval_trace, config
import asyncio




def load_chat_page(agent, config):
    """Load the chat page with the agent and configurations."""

    st.title("Ask Questions About Your PDF")

    

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    query = st.chat_input("Enter your question:")

    if query:
        st.chat_message("user").markdown(query)
        st.session_state.chat_history.append(HumanMessage(content=query))

        with st.chat_message("ai"):
            placeholder = st.empty()
            full_response = ""

            # for token in stream(query, agent):
            #     full_response += token
            #     placeholder.markdown(full_response + "▌")
            
            full_response = generate(query, agent, config)

            placeholder.markdown(full_response)
            asyncio.run(eval_trace(question = query,answer = full_response))
            st.session_state.chat_history.append(AIMessage(content=full_response))



if __name__ == "__main__":
    agent = agent_init()
    load_chat_page(agent, config)