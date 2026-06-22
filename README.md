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
   `python -m pip install -r requirements.txt`
3. Install and start Ollama.
4. Pull a local model:
   `ollama pull llama3:latest`
5. Put your documents into `data/docs/`.
6. Build the local index:
   `python scripts/build_index.py`
7. Start the app:
   `python run_demo.py`
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

### Windows prerequisites

Install these first on the Windows machine:

1. Python 3.11 or newer from python.org
2. Ollama for Windows
3. The local model used by the demo:
   `ollama pull llama3:latest`

When installing Python on Windows, make sure:

- `Add python.exe to PATH` is selected during install, or
- the `py` launcher is available in PowerShell / Command Prompt

### Run directly on Windows

1. Open PowerShell in the project folder.
2. Run:
   `run_windows.bat`

This script will:

- create `.venv` if it does not exist
- install or update required Python packages
- build the local index from `data\docs`
- start the web app
- open the browser automatically

You can also run the steps manually in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\build_index.py
python run_demo.py
```

Then open:

```text
http://127.0.0.1:8000
```

### Build a Windows executable package

1. Install Python on the Windows build machine.
2. Install Ollama and pull the model:
   `ollama pull llama3:latest`
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

### Windows troubleshooting

If the demo does not start correctly on Windows, check these first:

1. `py` is available:
   `py --version`
2. Ollama is installed and running:
   `ollama list`
3. The model exists locally:
   `ollama pull llama3:latest`
4. The index can be rebuilt manually:
   `python scripts\build_index.py`
5. The app starts manually:
   `python run_demo.py`

Common fixes:

- If PowerShell blocks virtual environment activation, run:
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- If port 8000 is already used, stop the other local app using that port first.
- If Ollama is not running, the UI still opens but responses fall back to retrieval-only mode.
- If you add new documents and do not see them reflected, use the `Rebuild Index` button in the UI.
