@echo off
cd /d "%~dp0"
echo Starting DeltaForceTool as Administrator...
echo.
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%CD%\" && echo Starting DeltaForceTool... && uv run main.py app && echo Press any key to exit...' -Verb RunAs"