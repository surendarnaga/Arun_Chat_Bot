# Manufacturing RAG Demo

Small local demo for a manufacturing knowledge assistant using:
- local document retrieval over PDF, DOCX, TXT and Markdown
- local Llama generation via Ollama
- simple browser chat UI

## What this demo does

- indexes documents from `data/docs/`
- chunks text into searchable passages
- retrieves relevant passages with TF-IDF similarity
- sends the question plus retrieved evidence to a local Ollama model
- shows answer with citations in a simple web UI

## Demo queries

- Find the report related to lantern clip issues
- Summarize the validation findings for split leather
- Where is the latest know-how document from Martin

## Quick start

1. Create a Python virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Install and start Ollama.
4. Pull a local model:
   `ollama pull llama3.1:8b`
5. Put your documents into `data/docs/`.
6. Build the local index:
   `python scripts/build_index.py`
7. Start the app:
   `uvicorn app.main:app --reload`
8. Open:
   `http://127.0.0.1:8000`

## Notes

- This is a demo. It uses TF-IDF retrieval for simplicity, not a production vector database.
- For a manager demo, this is enough to show the full RAG flow end to end.
- If Ollama is unavailable, the app still returns the best matching chunks so you can demonstrate retrieval.

## Reference Material

- The file `data/Manufacturing_Local_Llama_RAG_Jun2026.html` is kept in the repo as a reference document for the broader standalone manufacturing RAG concept and cost model.
- It is reference material only. The running demo indexes documents from `data/docs/` and writes its search index into `data/index/`.

## Windows runnable package

If you want to deploy this to a Windows machine as a small software package, use the included launcher and build scripts.

### Run directly on Windows

1. Install Python and Ollama.
2. Pull the model:
   `ollama pull llama3.1:8b`
3. Double-click `run_windows.bat`

This creates a virtual environment if needed, installs dependencies, starts the app and opens the browser.

### Build a Windows executable package

1. Install Python on the Windows build machine.
2. Install Ollama and pull the model:
   `ollama pull llama3.1:8b`
3. Double-click `build_windows.bat`
4. After the build completes, take the folder:
   `dist\ManufacturingRAGDemo`
5. Copy that folder to the target Windows machine.
6. Run:
   `ManufacturingRAGDemo.exe`

### Packaged runtime behavior

- The executable opens the UI in the browser automatically.
- Documents are read from `data\docs` next to the executable.
- The local search index is written to `data\index` next to the executable.
- Sample demo documents are copied into `data\docs` on first run if that folder is empty.
- Ollama must be installed and running on the Windows machine because the demo calls `http://127.0.0.1:11434`.
