@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt >nul
python run_demo.py
endlocal
