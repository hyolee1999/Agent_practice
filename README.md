# PDF RAG Assistant

A Streamlit application for uploading PDF documents and asking questions about
their contents. The project uses semantic chunking, hybrid dense and sparse
retrieval, Cohere reranking, and a DeepSeek-powered LangChain agent to produce
answers grounded in the indexed documents.

## Live Demo

Try the deployed application at
[agentpractice.streamlit.app](https://agentpractice.streamlit.app/).

## Features

- Upload and index multiple PDF files from a browser
- Extract PDF text with PyMuPDF
- Split documents into semantically related chunks
- Store and retrieve chunks from Qdrant using hybrid search
- Combine BGE dense embeddings with BM25 sparse embeddings
- Rerank retrieved passages with Cohere
- Stream generated answers in a chat interface
- Keep chat history in memory for the current application session

## How It Works

1. A user uploads one or more PDFs on the **Import PDF to Qdrant** page.
2. The application extracts each PDF's text and creates semantic chunks.
3. Dense and sparse representations are stored in the Qdrant
   `document_collection` collection.
4. On the **Ask question** page, the agent searches the collection using hybrid
   retrieval.
5. Cohere reranks the retrieved passages and DeepSeek generates a streamed
   response using the most relevant context.

## Technology Stack

- Python 3.13+
- Streamlit
- LangChain and LangGraph
- Qdrant
- FastEmbed (`BAAI/bge-small-en-v1.5` and `Qdrant/bm25`)
- Cohere Rerank (`rerank-english-v3.0`)
- DeepSeek Chat
- PyMuPDF
- `uv` for dependency and environment management

## Prerequisites

Before running the application, install or obtain:

- [Python 3.13 or later](https://www.python.org/downloads/)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- A running [Qdrant](https://qdrant.tech/documentation/quickstart/) instance
- A DeepSeek API key
- A Cohere API key

Docker can be used to start Qdrant locally:

```bash
docker run --name pdf-rag-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/hyolee1999/Agent_practice.git
cd Agent_practice
```

Install the locked dependencies:

```bash
uv sync
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Then configure the values required by the current implementation:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=http://localhost:6333

# Required only when connecting to an authenticated Qdrant instance.
QDRANT_API_KEY=
```

The OpenAI and Anthropic variables currently present in `.env.example` are not
used by the active application code.

## Running the Application

Start the Streamlit server from the project root:

```bash
uv run streamlit run src/main_page.py
```

Open <http://localhost:8501> if Streamlit does not open the application
automatically.

Use the application in this order:

1. Open **Import PDF to Qdrant**, choose one or more PDFs, and select **Submit**.
2. Wait for every file to be indexed.
3. Open **Ask question** and enter a question about the uploaded content.

## Project Structure

```text
.
├── notebook/                 # RAG experiments and prototype notebooks
├── src/
│   ├── agent/
│   │   ├── llm.py            # Agent invocation and response streaming
│   │   └── prompt.py         # Agent system prompt and response schema
│   ├── ingestion/
│   │   ├── chunker.py        # Semantic and fixed-size chunking helpers
│   │   ├── ingestion_manager.py
│   │   └── pdf_loader.py     # PDF loading with PyMuPDF
│   ├── page/
│   │   ├── chat.py           # Document question-and-answer page
│   │   └── upload.py         # PDF upload and indexing page
│   ├── rag/
│   │   ├── embeddings.py     # Dense and sparse embedding models
│   │   └── vector_store.py   # Qdrant collection and indexing logic
│   ├── main.py               # Retriever and agent initialization
│   └── main_page.py          # Streamlit navigation entry point
├── .env.example              # Environment variable template
├── pyproject.toml            # Project metadata and dependencies
└── uv.lock                   # Reproducible dependency lockfile
```

## Configuration

The active implementation uses the following defaults:

| Setting | Default | Location |
| --- | --- | --- |
| Qdrant collection | `document_collection` | `src/rag/vector_store.py` |
| Dense embedding model | `BAAI/bge-small-en-v1.5` | `src/rag/embeddings.py` |
| Sparse embedding model | `Qdrant/bm25` | `src/rag/embeddings.py` |
| Retrieved chunks | `4` | `src/main.py` |
| Reranked chunks | `1` | `src/main.py` |
| Chat model | `deepseek-chat` | `src/main.py` |

## Current Limitations

- All uploaded PDFs share one Qdrant collection; there is no per-user or
  per-document isolation.
- Re-uploading a PDF can create duplicate indexed chunks.
- Chat state uses an in-memory checkpointer and is lost when the app restarts.
- The application does not currently display citations or source page numbers in
  generated answers.
- PDF validation and user-facing indexing error details are limited.

## Troubleshooting

### Qdrant connection errors

Confirm that Qdrant is running and that `QDRANT_URL` points to it. For the local
Docker command above, use `http://localhost:6333`.

### Authentication or model errors

Confirm that both `DEEPSEEK_API_KEY` and `COHERE_API_KEY` are present in `.env`
and valid. Restart Streamlit after changing environment variables.

### Dev Container Python version

The current `.devcontainer/devcontainer.json` references Python 3.11, while
`pyproject.toml` requires Python 3.13 or later. Use a Python 3.13 environment, or
update the dev-container image before installing the project there.

## License

No license file is currently included. Unless a license is added, the repository
is not automatically licensed for redistribution or modification.
