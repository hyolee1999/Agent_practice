import streamlit as st
import tempfile
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.tools import create_retriever_tool
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from rag.embeddings import sparse_embeddings, dense_embeddings
from qdrant_client import QdrantClient, models
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from langchain_core.documents import Document
from dotenv import load_dotenv
from rag.vector_store import retriever_init, index_pdf_documents, client
from agent.prompt import SYSTEM_PROMPT, ResponseFormat
from agent.llm import generate, stream
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from langchain_cohere import CohereRerank
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from eval.metrics import score_with_ragas, init_ragas_metrics
from rag.embeddings import dense_embeddings
from eval.metrics import metrics
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langfuse import get_client
from langfuse.langchain import CallbackHandler


load_dotenv()

# Initialize Langfuse client for logging
langfuse_client = get_client()
langfuse_callback = CallbackHandler()
context_manager = []

config = {'configurable':{'thread_id':'1'}, "callbacks": [langfuse_callback]}

@wrap_tool_call
def intercept_retriever(request: ToolCallRequest, handler):
    # messages = request.state["messages"]   # full history, available here
        

    result = handler(request)   # actually executes the tool

    if request.tool_call["name"] == "document_retriever":
        context_manager.append(result.content)

    # post-process result using context from messages if needed
    return result


@st.cache_resource()
def agent_init():

    model = init_chat_model(model="deepseek-chat", temperature=0.1)

    init_ragas_metrics(metrics ,llm=model, embedding=dense_embeddings)
    
    checkpointer = InMemorySaver()

    # config = {'configurable': {'thread_id': str(uuid4())}}

    qdrant = retriever_init(
        collection_name="document_collection"
    )

    retriever = qdrant.as_retriever(search_kwargs={"k": 4})

    compressor =  CohereRerank(model="rerank-english-v3.0", top_n = 1)

    compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

    retriever_tool = create_retriever_tool(
        compression_retriever,
        "document_retriever",
        description="Search for relevant documents to answer user questions",
    )


    agent = create_agent(
        model=model,
        tools=[retriever_tool],
        middleware= [intercept_retriever],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )
    return agent

async def eval_trace(question, answer, context = context_manager):

    print("question: ", question)
    print("answer: ", answer)
    print("context: ", context)
    with langfuse_client.start_as_current_observation(as_type="span", name="rag") as trace:
        # Store trace_id for later use
        trace_id = trace.trace_id
        # retrieve the relevant chunks
        # chunks = get_similar_chunks(question)
        # pass it as span
        with trace.start_as_current_observation(
            name="retrieval",
            input={'question': question},
            output={'contexts': context}
        ):
            pass
        # use llm to generate a answer with the chunks
        # answer = get_response_from_llm(question, chunks)
        with trace.start_as_current_observation(
            name="generation",
            input={'question': question, 'contexts': context},
            output={'answer': answer}
        ):
            pass
        # compute scores for the question, context, answer tuple
        ragas_scores = await score_with_ragas(question, context, answer)
    
    for m in metrics:
        langfuse_client.create_score(
            name=m.name,
            value=ragas_scores[m.name],
            trace_id=trace_id
        )
    context_manager.clear()
    



