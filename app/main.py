from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .rag import (
    ALLOWED_EXTENSIONS,
    DOCS_DIR,
    IndexNotBuiltError,
    STATIC_DIR,
    answer_question,
    build_index,
    ensure_runtime_dirs,
    list_documents,
    seed_sample_docs,
)

app = FastAPI(title="Manufacturing RAG Demo")
STATIC_HTML = STATIC_DIR / "index.html"

ensure_runtime_dirs()
seed_sample_docs()


class ChatRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)
    model: str = Field(default="llama3:latest")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_HTML)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/documents")
def documents() -> dict[str, object]:
    items = list_documents()
    return {
        "count": len(items),
        "documents": items,
    }


@app.post("/api/reindex")
def reindex() -> dict[str, int | str]:
    index = build_index()
    return {
        "status": "ok",
        "chunks": len(index.get("chunks", [])),
    }


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)) -> dict[str, object]:
    ensure_runtime_dirs()
    saved_files: list[str] = []

    for upload_file in files:
        filename = Path(upload_file.filename or "").name
        if not filename:
            continue

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for {filename}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        target_path = DOCS_DIR / filename
        content = await upload_file.read()
        target_path.write_bytes(content)
        saved_files.append(filename)

    if not saved_files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    index = build_index()
    return {
        "status": "ok",
        "uploaded": saved_files,
        "document_count": len(list_documents()),
        "chunks": len(index.get("chunks", [])),
    }


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    try:
        return answer_question(
            question=payload.question,
            top_k=payload.top_k,
            model=payload.model,
        )
    except IndexNotBuiltError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
