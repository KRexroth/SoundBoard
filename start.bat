@echo off
cd /d "%~dp0"
python serve.py
if errorlevel 1 (
    echo.
    echo Something went wrong -- is Python installed? Get it from python.org
    pause
)
