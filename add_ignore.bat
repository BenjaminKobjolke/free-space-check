@echo off
if "%~1"=="" (
    echo Usage: add_ignore.bat PATH
    echo Example: add_ignore.bat C:\Users\XIDA\AppData\Local\BraveSoftware
    pause
    exit /b 1
)
call uv run free-space-check --add-ignore "%*"
pause
