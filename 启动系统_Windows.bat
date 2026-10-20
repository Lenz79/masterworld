@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 (
 echo Dependency install failed. Check your network or Python installation.
 pause
 exit /b 1
)
python server.py
pause
