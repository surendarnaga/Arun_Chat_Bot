from __future__ import annotations

import json
import math
import pickle
import re
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docx import Document
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SOURCE_DIR = Path(__file__).resolve().parent.parent
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", SOURCE_DIR))
APP_HOME = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else SOURCE_DIR
STATIC_DIR = BUNDLE_DIR / "static"
SAMPLE_DOCS_DIR = BUNDLE_DIR / "sample_docs"
DOCS_DIR = APP_HOME / "data" / "docs"
INDEX_DIR = APP_HOME / "data" / "index"
INDEX_FILE = INDEX_DIR / "tfidf_index.pkl"
DEFAULT_MODEL = "llama3.1:8b"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
QUERY_ALIASES = {
    "lanten": "lantern",
    "s[lit": "split",
    "know how": "know-how",
}


@dataclass
class Chunk:
    chunk_id: str
    source: str
    title: str
    text: str


class IndexNotBuiltError(RuntimeError):
    pass


def ensure_runtime_dirs() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def seed_sample_docs() -> None:
    ensure_runtime_dirs()
    if any(DOCS_DIR.iterdir()) or not SAMPLE_DOCS_DIR.exists():
        return

    for sample_file in SAMPLE_DOCS_DIR.iterdir():
        if sample_file.is_file():
            shutil.copy2(sample_file, DOCS_DIR / sample_file.name)


def relative_source_path(path: Path) -> str:
    for base in (APP_HOME, SOURCE_DIR, BUNDLE_DIR):
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_query(text: str) -> str:
    normalized = normalize_text(text).lower()
    for source, target in QUERY_ALIASES.items():
        normalized = normalized.replace(source, target)
    normalized = normalized.replace("[", "")
    return normalized


def load_text_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    if suffix == ".docx":
        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return ""


def chunk_text(text: str, source: str, title: str, chunk_size: int = 1200, overlap: int = 200) -> list[Chunk]:
    clean = normalize_text(text)
    if not clean:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 1
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        snippet = clean[start:end].strip()
        if snippet:
            chunks.append(
                Chunk(
                    chunk_id=f"{Path(source).stem}-{index}",
                    source=source,
                    title=title,
                    text=snippet,
                )
            )
        if end >= len(clean):
            break
        start = max(end - overlap, start + 1)
        index += 1
    return chunks


def discover_chunks() -> list[Chunk]:
    ensure_runtime_dirs()
    chunks: list[Chunk] = []
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        text = load_text_from_path(path)
        rel = relative_source_path(path)
        chunks.extend(chunk_text(text=text, source=rel, title=path.name))
    return chunks


def build_index() -> dict[str, Any]:
    ensure_runtime_dirs()
    chunks = discover_chunks()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    texts = [chunk.text for chunk in chunks]
    matrix = vectorizer.fit_transform(texts) if texts else None
    payload = {
        "chunks": chunks,
        "vectorizer": vectorizer,
        "matrix": matrix,
    }
    with INDEX_FILE.open("wb") as handle:
        pickle.dump(payload, handle)
    return payload


def load_index() -> dict[str, Any]:
    if not INDEX_FILE.exists():
        raise IndexNotBuiltError("Index does not exist. Run the build step first.")
    with INDEX_FILE.open("rb") as handle:
        return pickle.load(handle)


def retrieve(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    index = load_index()
    chunks: list[Chunk] = index["chunks"]
    vectorizer: TfidfVectorizer = index["vectorizer"]
    matrix = index["matrix"]

    if not chunks or matrix is None:
        return []

    query_vector = vectorizer.transform([normalize_query(query)])
    similarities = cosine_similarity(query_vector, matrix).flatten()
    ranked_indices = similarities.argsort()[::-1][:top_k]

    results: list[dict[str, Any]] = []
    for i in ranked_indices:
        score = float(similarities[i])
        if math.isclose(score, 0.0):
            continue
        chunk = chunks[int(i)]
        results.append(
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "title": chunk.title,
                "text": chunk.text,
                "score": round(score, 4),
            }
        )
    return results


def build_prompt(question: str, results: list[dict[str, Any]]) -> str:
    context_lines = []
    for idx, result in enumerate(results, start=1):
        context_lines.append(
            f"Source {idx}: {result['title']} ({result['source']})\n"
            f"Relevance: {result['score']}\n"
            f"Content:\n{result['text']}"
        )

    context = "\n\n".join(context_lines)
    return (
        "You are a manufacturing knowledge assistant. "
        "Answer only from the supplied sources. "
        "If the sources are weak or missing, say that clearly. "
        "Always provide a concise answer followed by cited sources.\n\n"
        f"Question: {question}\n\n"
        f"Sources:\n{context}"
    )


def ask_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Answer only from retrieved sources and cite them."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.1},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
            message = payload.get("message", {})
            return message.get("content")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def answer_question(question: str, top_k: int = 5, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    results = retrieve(question=question, top_k=top_k)
    if not results:
        return {
            "answer": "No relevant content was found in the indexed documents.",
            "citations": [],
            "mode": "retrieval-only",
        }

    prompt = build_prompt(question=question, results=results)
    answer = ask_ollama(prompt=prompt, model=model)
    if not answer:
        fallback = "I could not reach the local Llama model, but these are the most relevant matching passages."
        return {
            "answer": fallback,
            "citations": results,
            "mode": "retrieval-only",
        }

    return {
        "answer": answer,
        "citations": results,
        "mode": "rag",
    }
