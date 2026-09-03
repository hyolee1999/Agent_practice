"""Pure Python factory for creating the Document RAG Agent (Framework-agnostic)."""

from typing import Optional, List, Any
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from docuagent.config.settings import settings
from docuagent.rag.embeddings import dense_embeddings
from docuagent.agent.prompts import SYSTEM_PROMPT
from docuagent.agent.tools import create_document_retriever_tool
from docuagent.observability.langfuse import intercept_retriever
from docuagent.observability.metrics import init_ragas_metrics, default_metrics


def create_rag_agent(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    tools: Optional[List[Any]] = None,
    middleware: Optional[List[Any]] = None,
    checkpointer: Optional[Any] = None,
    init_eval_metrics: bool = True,
):
    """Instantiate and configure the LangChain/LangGraph RAG Agent.

    This function is completely decoupled from any UI framework (Streamlit / FastAPI).
    """
    model_id = model_name or settings.default_model
    temp = temperature if temperature is not None else settings.temperature

    # Initialize chat model
    model = init_chat_model(model=model_id, temperature=temp)

    # Initialize Ragas evaluation metrics with the model and embeddings
    if init_eval_metrics:
        init_ragas_metrics(default_metrics, llm=model, embedding=dense_embeddings)

    # Configure tools
    agent_tools = tools if tools is not None else [create_document_retriever_tool()]

    # Memory checkpointer
    agent_checkpointer = checkpointer if checkpointer is not None else InMemorySaver()

    # Tool execution middleware (for Langfuse context capture)
    agent_middleware = middleware if middleware is not None else [intercept_retriever]

    # Create agent
    agent = create_agent(
        model=model,
        tools=agent_tools,
        middleware=agent_middleware,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=agent_checkpointer,
    )

    return agent
