@echo off
cd /d "%~dp0"

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
  echo Python 3.12 was not found in the default install location.
  echo Please install Python 3.12 first, then run this script again.
  pause
  exit /b 1
)

start "" "%PYTHON_EXE%" server.py
start "" http://127.0.0.1:8000

echo Starting Proofline at http://127.0.0.1:8000
