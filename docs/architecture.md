# DocuAgent AI — System Architecture & Design Guide

## 1. Overview
DocuAgent AI is a production-grade Document Retrieval-Augmented Generation (RAG) agent featuring:
- **Hybrid Vector Search**: Dense semantic embeddings (`BAAI/bge-small-en-v1.5`) combined with Sparse keyword search (`Qdrant/bm25`) powered by Qdrant.
- **Reranking**: Contextual compression reranking via Cohere (`rerank-english-v3.0`).
- **Agentic Workflow**: Dynamic tool calling via LangGraph / LangChain agents.
- **Full Observability**: End-to-end tracing via Langfuse.
- **Continuous Evaluation**: Quality monitoring via Ragas (`faithfulness`, `answer_relevancy`, `llm_context_precision_without_reference`).

### Two Targeted Delivery Versions:
1. 🧪 **Streamlit Version (`docuagent.ui`) — Quick Prototyping & Visual R&D**:
   - Built for rapid experimentation, PDF ingestion testing, and reviewing Ragas evaluation badges in real time in the UI.
2. 🚀 **FastAPI Version (`docuagent.api`) — Actual Production Implementation**:
   - Built for the actual production service implementation: asynchronous non-blocking request handling, Server-Sent Events (SSE) token streaming, REST API endpoints, OpenAPI documentation, and serving custom web frontends.

---

## 2. Directory Hierarchy

```text
src/docuagent/
├── config/             # Settings loaded via Pydantic BaseSettings (.env)
├── ingestion/          # PDF extraction and semantic/fixed chunking
├── rag/                # Embeddings and hybrid Qdrant vector store
├── agent/              # Prompts, retriever tool, agent factory, and execution
├── observability/      # Langfuse client, context interception, and Ragas metrics
├── api/                # FastAPI application, CORS, static mounting, and routes
└── ui/                 # Streamlit application, multipage navigation, and UI caching
```

---

## 3. Layer Responsibilities & Decoupling

| Layer | Responsibility | Dependencies |
|---|---|---|
| `config` | Type-safe settings from `.env` | `pydantic-settings` |
| `ingestion` | Load raw PDFs into `Document` chunks | `pymupdf`, `langchain-text-splitters` |
| `rag` | Vector storage, indexing, and hybrid retrieval | `qdrant-client`, `langchain-qdrant`, `fastembed` |
| `agent` | RAG agent construction, prompts, execution | `langchain`, `langgraph`, `langchain-cohere` |
| `observability`| Langfuse tracing and Ragas scoring | `langfuse`, `ragas` |
| `api` | REST / SSE streaming endpoints & web UI | `fastapi`, `uvicorn` |
| `ui` | Streamlit interactive web interface & cached loaders | `streamlit` |

> **Key Architectural Rule**: Core domain layers (`config`, `ingestion`, `rag`, `agent`, `observability`) **never** import Streamlit. Streamlit caching (`@st.cache_resource`) is strictly isolated inside `docuagent.ui.cache`.

---

## 4. Execution Commands

### Running FastAPI Backend
```bash
uv run uvicorn docuagent.api.app:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Web Interface: `http://localhost:8000/`

### Running Streamlit UI
```bash
uv run streamlit run src/docuagent/ui/app.py
```
- Streamlit Interface: `http://localhost:8501`

### Running Automated Test Suite
```bash
uv run pytest tests/
```
