"""Chat endpoints supporting JSON and Server-Sent Events (SSE) streaming."""

from docuagent.observability.metrics import eval_trace
import json
import asyncio
from typing import AsyncGenerator, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from docuagent.agent.factory import create_rag_agent
from docuagent.agent.execution import generate, stream
from docuagent.observability.langfuse import get_agent_config, context_manager


router = APIRouter(prefix="/api", tags=["chat"])

# Module-level cached agent fo r API worker process
_api_agent = None

def get_or_create_agent(**kwargs):
    """Lazily instantiate the RAG agent for the API server."""
    global _api_agent
    if _api_agent is None:
        kwargs["init_eval_metrics"] = True
        _api_agent = create_rag_agent(**kwargs)
        _context_manager = context_manager
    return _api_agent


class ChatRequest(BaseModel):
    query: str
    session_id: str


class ChatResponse(BaseModel):
    query: str
    response: str
    status: str = "success"


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Standard non-streaming chat endpoint returning JSON."""
    query = request.query.strip()
    thread_id = request.session_id
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        agent = get_or_create_agent()
        answer = generate(query, agent, config=get_agent_config(thread_id = thread_id))
        await eval_trace(question=query, answer=answer)
        return ChatResponse(query=query, response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/chat/stream")
@router.get("/chat/stream")
async def chat_stream_endpoint(
    request: Optional[ChatRequest] = None,
    query: Optional[str] = None,
):
    """Server-Sent Events (SSE) streaming chat endpoint (accepts POST JSON or GET query parameter)."""
    user_query = ""
    if request and request.query:
        user_query = request.query.strip()
    elif query:
        user_query = query.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            agent = get_or_create_agent()
            config = get_agent_config(thread_id = request.session_id)

            full_answer = []
            for token in stream(user_query, agent, config=config):
                if token:
                    full_answer.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0.01)
            complete_text = "".join(full_answer)
            await eval_trace(question=user_query, answer=complete_text)
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_json = json.dumps({"error": str(e)})
            yield f"data: {err_json}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
