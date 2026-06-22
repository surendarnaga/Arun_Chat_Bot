from __future__ import annotations

import threading
import webbrowser

import uvicorn

from app.main import app
from app.rag import ensure_runtime_dirs, seed_sample_docs


def open_browser() -> None:
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    ensure_runtime_dirs()
    seed_sample_docs()
    threading.Timer(1.2, open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
