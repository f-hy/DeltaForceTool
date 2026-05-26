# Hotkey Troubleshooting

## Problem: Alt+S hotkey not working in other applications

The `keyboard` library requires **administrator privileges** to register global hotkeys that work across all applications.

### Solution 1: Run as Administrator (Recommended)

1. Right-click on the terminal/IDE
2. Select "Run as administrator"
3. Run: `uv run main.py`

### Solution 2: Create a batch file

Create a file `run_as_admin.bat` in the project root:

```batch
@echo off
cd /d "%~dp0"
python -m pip install keyboard >nul 2>&1
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%CD%\" && uv run main.py' -Verb RunAs"
```

### Solution 3: Use alternative library

Install `pynput` which may have better compatibility:

```bash
pip install pynput
```

Then modify `global_hotkey.py` to use pynput instead.

### Solution 4: Manual click (Fallback)

If hotkeys don't work, you can:
1. Click the small DeltaForceTool window
2. Use keyboard shortcuts within the app
3. Or click "File > Exit" to exit

## Exit Hotkey Issues

If `Ctrl+Alt+Q` doesn't exit the app:
- Use the File menu: File > Exit
- Or close the small window directly
