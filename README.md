# DocuAgent AI — Document RAG Agent

A production-grade Document Retrieval-Augmented Generation (RAG) system with hybrid vector search, Cohere reranking, agentic tool calling, Langfuse tracing, and continuous Ragas evaluation.

This project provides **two distinct deployment versions** sharing the same unified core domain engine:

1. 🧪 **Streamlit Version (Quick Prototyping & R&D)**:
   - Designed for fast visual experimentation, document upload testing, and inspecting turn-by-turn **Ragas evaluation scores** (`faithfulness`, `answer_relevancy`, `llm_context_precision_without_reference`) directly in the UI.
2. 🚀 **FastAPI Version (Production-Ready Implementation)**:
   - Designed for the actual real-world service implementation with high-performance async handling, **Server-Sent Events (SSE) token streaming**, clean REST endpoints, OpenAPI Swagger documentation, and serving standalone web frontends.

---

## Key Features

- **Shared Core Engine**: Both Streamlit and FastAPI share the same framework-agnostic `docuagent` package (`rag`, `agent`, `ingestion`, `observability`).
- **Hybrid Vector Search**: Combines Dense semantic embeddings (`BAAI/bge-small-en-v1.5`) with Sparse BM25 keyword search (`Qdrant/bm25`) in Qdrant.
- **Contextual Reranking**: Reranks top candidates using Cohere (`rerank-english-v3.0`) to maximize signal-to-noise ratio.
- **Agentic Tool Calling**: Powered by LangGraph / LangChain agents dynamically querying document indices.
- **Deep Observability**: End-to-end trace tracking with **Langfuse**, capturing retrieval chunks, LLM prompts, token consumption, and latency.
- **Automated RAG Evaluation**: Evaluates answers on every turn using **Ragas** metrics:
  - `faithfulness` (hallucination detection)
  - `answer_relevancy` (question alignment)
  - `llm_context_precision_without_reference` (retrieval precision)
- **Clean Architecture**: Domain logic is 100% decoupled from presentation layers — neither Streamlit nor FastAPI leaks runtime dependencies into the core business logic.

---

## Project Structure

```text
Agent_practice_clean/
├── docs/                                  # Architectural specs & technical notes
│   ├── architecture.md
│   └── llm_embedding_note.md
├── frontend/                              # Web application assets
│   └── dist/                              # HTML/JS client served by FastAPI
├── tests/                                 # Unit & integration test suite
│   ├── test_config.py
│   ├── test_embeddings.py
│   ├── test_agent_factory.py
│   └── test_ragas_parser.py
├── src/
│   ├── main.py                            # Backward-compatibility import shim
│   ├── main_page.py                       # Backward-compatibility Streamlit shim
│   └── docuagent/                         # Core Python Package
│       ├── config/                        # Pydantic BaseSettings (.env loading)
│       │   └── settings.py
│       ├── ingestion/                     # PDF loading & semantic/fixed chunking
│       │   ├── loader.py
│       │   ├── chunker.py
│       │   └── manager.py
│       ├── rag/                           # Qdrant vector store & embedding models
│       │   ├── embeddings.py
│       │   └── vector_store.py
│       ├── agent/                         # Prompts, tools, factory & execution
│       │   ├── prompts.py
│       │   ├── tools.py
│       │   ├── factory.py
│       │   └── execution.py
│       ├── observability/                 # Langfuse tracing & Ragas scoring
│       │   ├── langfuse.py
│       │   └── metrics.py
│       ├── api/                           # FastAPI web service & SSE routes
│       │   ├── app.py
│       │   └── routes/
│       │       ├── chat.py
│       │       └── documents.py
│       └── ui/                            # Streamlit application & cached loaders
│           ├── app.py
│           ├── cache.py
│           └── pages/
│               ├── upload.py
│               └── chat.py
├── app/main.py                            # FastAPI delegation shim
├── pyproject.toml                         # Packaging metadata & console scripts
└── uv.lock                                # Reproducible dependency lockfile
```

---

## Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [`uv`](https://docs.astral.sh/uv/) (recommended for dependency management)
- Running [Qdrant](https://qdrant.tech/) instance
- (Optional) Running [Langfuse](https://langfuse.com/) instance for telemetry

### Start Services with Docker:

```bash
# 1. Start Qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 2. (Optional) Start Langfuse self-hosted
# See https://langfuse.com/docs/deployment/local
```

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hyolee1999/Agent_practice.git
   cd Agent_practice
   ```

2. **Install dependencies and editable package**:
   ```bash
   uv sync
   uv pip install -e .
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Fill in your API keys:
   ```dotenv
   # LLM Providers (Configure at least one)
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   COHERE_API_KEY=your_cohere_api_key

   # Vector Store
   QDRANT_URL=http://localhost:6333
   QDRANT_API_KEY=

   # Observability (Langfuse)
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_BASE_URL=http://localhost:3000
   ```

---

## Running the Applications

Choose the version suited to your workflow:

### Version 1: Streamlit UI (Quick Prototype & Evaluation)
> **Use Case**: Fast local experimentation, testing PDF uploads, and viewing Ragas quality scores (`faithfulness`, `relevancy`, `precision`) live in the UI after every message.

```bash
uv run streamlit run src/docuagent/ui/app.py
```
*(or via backward-compatible shortcut: `uv run streamlit run src/main_page.py`)*

- **Interface URL**: `http://localhost:8501`
- **Workflow**:
  1. Open the **Upload Documents** page, choose your PDF files, and click **Index Documents**.
  2. Switch to **Chat & Evaluate** to interact with the agent.
  3. Expand the **Evaluation** badge beneath any response to inspect real-time Ragas scores logged to Langfuse.

---

### Version 2: FastAPI Backend (Actual Implementation & API Serving)
> **Use Case**: Production implementation providing asynchronous REST APIs, Server-Sent Events (SSE) streaming token output, and serving standalone web applications.

```bash
uv run uvicorn docuagent.api.app:app --reload --port 8000
```
*(or via console script: `uv run docuagent-api`)*

- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Alternative ReDoc Docs**: `http://localhost:8000/redoc`
- **Integrated Web Frontend**: `http://localhost:8000/` (served from `frontend/dist`)

---

## API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Synchronous JSON chat (`{"query": "..."}`) |
| `POST` / `GET` | `/api/chat/stream` | Server-Sent Events (SSE) streaming token output |
| `POST` | `/api/upload` | Upload PDF file and index into Qdrant |
| `POST` | `/api/clear` | Reset active conversation session |
| `GET` | `/docs` | OpenAPI / Swagger interactive documentation |

---

## Automated Test Suite

Run the test suite using Python's discoverable test runner:
```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

Tested areas:
- `test_config.py`: Validates environment settings & defaults.
- `test_embeddings.py`: Checks 384-dim dense and sparse vector generation.
- `test_agent_factory.py`: Verifies pure Python agent construction without Streamlit runtime warnings.
- `test_ragas_parser.py`: Verifies robust JSON extraction from markdown code fences (` ```json `).

---

## Configuration Reference

Settings are managed via `pydantic-settings` in [src/docuagent/config/settings.py](file:///Users/khoa/Agent_practice_clean/src/docuagent/config/settings.py):

| Setting | Env Variable | Default | Purpose |
|---|---|---|---|
| `qdrant_url` | `QDRANT_URL` | `http://localhost:6333` | Vector database endpoint |
| `collection_name` | — | `document_collection` | Qdrant hybrid collection |
| `dense_embedding_model` | — | `BAAI/bge-small-en-v1.5` | Dense vector model |
| `sparse_embedding_model` | — | `Qdrant/bm25` | Sparse keyword model |
| `default_model` | — | `anthropic:claude-sonnet-4-6` | LLM for agent and evaluation |
| `rerank_model` | — | `rerank-english-v3.0` | Cohere reranker |
| `top_k` | `TOP_K` | `4` | Retrieval candidate count |

---

## Documentation

- **[System Architecture Guide](file:///Users/khoa/Agent_practice_clean/docs/architecture.md)**: Deep dive into the layered architecture, design principles, and decoupling guidelines.
- **[Embedding Notes](file:///Users/khoa/Agent_practice_clean/docs/llm_embedding_note.md)**: Notes on vector dimensions and model selection.
