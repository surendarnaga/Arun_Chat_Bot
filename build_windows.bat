@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --clean manufacturing_rag_demo.spec

echo.
echo Build complete.
echo Output folder: dist\ManufacturingRAGDemo
endlocal
