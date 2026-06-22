@echo off
setlocal
cd /d %~dp0
set PYTHONUTF8=1

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\build_index.py
python run_demo.py
endlocal
