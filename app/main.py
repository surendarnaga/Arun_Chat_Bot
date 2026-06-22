from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .rag import IndexNotBuiltError, STATIC_DIR, answer_question, build_index, ensure_runtime_dirs, seed_sample_docs

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


@app.post("/api/reindex")
def reindex() -> dict[str, int | str]:
    index = build_index()
    return {
        "status": "ok",
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
