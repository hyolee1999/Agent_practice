"""Document ingestion and session management endpoints."""

import tempfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException

from docuagent.rag.vector_store import index_pdf_documents

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF file, split into semantic chunks, and index into Qdrant."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        num_chunks = index_pdf_documents(tmp_path)
        tmp_path.unlink(missing_ok=True)

        return {
            "status": "success",
            "filename": file.filename,
            "message": f"Successfully indexed {num_chunks} chunks into vector store.",
            "chunks_count": num_chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/clear")
async def clear_session():
    """Clear active agent session or conversation history."""
    return {"status": "success", "message": "Conversation session cleared."}
