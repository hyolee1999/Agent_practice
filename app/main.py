import os
import sys
import tempfile
import asyncio
from pathlib import Path
from typing import AsyncGenerator

# Ensure 'src' is available in Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from main import agent_init

load_dotenv()

app = FastAPI(
    title="DocuAgent AI API",
    description="FastAPI Backend for Document RAG Agent with Streaming and Hybrid Search",
    version="1.0.0",
)

# Enable CORS for local testing / external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/assets") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Request Models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    query: str
    response: str
    status: str = "success"


# Optional: Lazy load or initialize RAG components from src/
agent_instance = None

def get_or_create_agent():
    """Initializes LangChain/LangGraph agent from existing project modules."""
    global agent_instance
    if agent_instance is None:
        try:
            from langchain.chat_models import init_chat_model
            from langchain.agents import create_agent
            from langchain_core.tools import create_retriever_tool
            from langgraph.checkpoint.memory import InMemorySaver
            from langchain_cohere import CohereRerank
            from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
            from rag.vector_store import retriever_init
            from agent.prompt import SYSTEM_PROMPT

            model = init_chat_model(model="deepseek-chat", temperature=0.1)
            checkpointer = InMemorySaver()

            qdrant = retriever_init(collection_name="document_collection")
            retriever = qdrant.as_retriever(search_kwargs={"k": 4})

            compressor = CohereRerank(model="rerank-english-v3.0", top_n=1)
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=retriever
            )

            retriever_tool = create_retriever_tool(
                compression_retriever,
                "document_retriever",
                description="Search for relevant documents to answer user questions",
            )

            agent_instance = create_agent(
                model=model,
                tools=[retriever_tool],
                system_prompt=SYSTEM_PROMPT,
                checkpointer=checkpointer,
            )
        except Exception as e:
            print(f"[Agent Init Warning] Could not initialize full RAG agent: {e}")
            agent_instance = None
    return agent_instance


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify backend status."""
    return {"status": "ok", "service": "DocuAgent AI Backend"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file, save it to a temporary path, and index into Qdrant."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            temp_pdf_path = tmp.name

        # Trigger indexing via src/rag/vector_store.py
        try:
            from rag.vector_store import index_pdf_documents
            index_pdf_documents(pdf_path=temp_pdf_path)
            message = f"Successfully indexed {file.filename} into vector store."
        except Exception as rag_err:
            print(f"[Indexing Warning] RAG indexer note: {rag_err}")
            message = f"Uploaded {file.filename} (Note: check Qdrant/API keys if indexing failed: {rag_err})"

        return {
            "status": "success",
            "filename": file.filename,
            "message": message,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Standard non-streaming chat endpoint."""
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    agent = get_or_create_agent()
    if agent:
        try:
            from agent.llm import generate
            answer = generate(query, agent)
            return ChatResponse(query=query, response=answer)
        except Exception as e:
            return ChatResponse(
                query=query,
                response=f"Agent error: {str(e)}. (Check if API keys in .env are configured).",
            )
    else:
        # Fallback / Demo response for testing
        return ChatResponse(
            query=query,
            response=f"FastAPI received your query: '{query}'. (Agent is running in practice mode).",
        )


@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Server-Sent Events (SSE) streaming chat endpoint."""
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    async def event_generator() -> AsyncGenerator[str, None]:
        agent = get_or_create_agent()
        if agent:
            try:
                from agent.llm import stream
                for token in stream(query, agent):
                    if token:
                        print("token from FastAPI:", token)
                        yield f"data: {token}\n\n"
                        await asyncio.sleep(0.01)
                yield "data: [DONE]\n\n"
                return
            except Exception as e:
                yield f"data: Agent streaming error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"
                return

        # Fallback simulated stream for quick testing
        sample_response = f"FastAPI streaming response for: '{query}'. You are connected to the FastAPI backend successfully!"
        for word in sample_response.split(" "):
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.04)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/clear")
async def clear_session():
    """Clear active agent session / memory."""
    global agent_instance
    agent_instance = None
    return {"status": "success", "message": "Conversation history cleared."}


# ---------------------------------------------------------------------------
# Static Files & Frontend Mount
# ---------------------------------------------------------------------------
DIST_DIR = ROOT_DIR / "dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

@app.get("/")
async def serve_index():
    """Serve frontend index.html."""
    index_file = DIST_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not found. Please verify dist/index.html exists."}
