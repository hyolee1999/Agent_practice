from typing import Generator

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.tools import create_retriever_tool
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from rag.vector_store import retriever_init
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient, models
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from ingestion.ingestion_manager import raw_to_documents
from langchain_core.documents import Document
from langchain_core.messages import AIMessageChunk
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest



def generate(query: str, agent, config) -> str:
    """Generate an answer to the query using the agent."""  
    result = agent.invoke(
        {
            'messages':[
                {
                    'role':'user',
                    'content': query
                }
            ]
        },
        config = config
    )

    # print(result)

    return result["messages"][-1].content

def stream(query: str, agent, config ) -> Generator[str, None, None]:
    """Stream the answer to the query using the agent."""

    for chunk in agent.stream(
        {
            'messages':[
                {
                    'role':'user',
                    'content': query
                }
            ]
        },
        config = config,
        stream_mode = "messages",
        version = "v2"
    ):
        # print(chunk)
        if chunk["type"] == "messages":
            token, metadata = chunk["data"]
            if token.content_blocks and isinstance(token, AIMessageChunk):
                if "text" in token.content_blocks[0]:
                    
                    yield token.content_blocks[0]["text"]
                yield ""  # Yield a space to indicate continuation
            yield ""  # Yield a space to indicate continuation




    














    










    