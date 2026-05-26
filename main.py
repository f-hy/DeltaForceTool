# -*- coding: UTF-8 -*-
"""
@file main.py
@author f-hy (friend0@qq.com)
@date 2026-05-22
@version 0.1
@brief DeltaForceTool entry point
@github https://github.com/f-hy
@copyright Copyright (c) 2026
"""

import sys
import os
import json

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from pathlib import Path

from deltaforcetool import TimeClockUI, TimeConfig
from deltaforcetool.tools.ocr.ocr_tool import OCRTool
from deltaforcetool.utils import print_mean


def load_config():
    """Load configuration from config files."""
    config_dir = Path(__file__).parent / "conf"
    config_file = config_dir / "keymap.json"

    default_config = {
        "hotkeys": {
            "ocr_trigger": "alt+s",
            "exit": "ctrl+alt+q"
        },
        "ocr_settings": {
            "overlay_alpha": 0.7,
            "rect_color": "#00ff00",
            "rect_width": 3,
            "rect_dash": [4, 2]
        }
    }

    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_config


def run_clock_only():
    """Run only the time clock UI."""
    config = TimeConfig(
        timezone="Asia/Shanghai",
        update_interval_ms=100
    )
    clock_ui = TimeClockUI(config)
    clock_ui.create_ui()


def run_main_app_with_ocr_shortcut():
    """Run main app with global hotkey from config to launch OCR tool."""
    config = load_config()
    hotkeys = config.get("hotkeys", {})
    ocr_key = hotkeys.get("ocr_trigger", "alt+s")
    exit_key = hotkeys.get("exit", "ctrl+alt+q")

    try:
        import keyboard
    except ImportError:
        print("Keyboard library not found. Installing...")
        os.system("pip install keyboard")
        import keyboard

    hotkey_ocr_registered = False
    hotkey_exit_registered = False
    exit_state = [False]
    input_thread_stopped = [False]

    # Create main window
    main_window = tk.Tk()
    main_window.title("DeltaForceTool")
    main_window.geometry("100x100")
    main_window.attributes('-topmost', True)

    label = tk.Label(main_window, text="DeltaForceTool\nPress {} for OCR".format(ocr_key.upper()),
                     font=("Consolas", 10))
    label.pack(pady=20)

    info = tk.Label(main_window, text="TimeClock: uv run main.py clock",
                    font=("Consolas", 8), fg="gray")
    info.pack(pady=10)

    status = tk.Label(main_window, text="Status: Initializing...",
                      font=("Consolas", 8), fg="orange")
    status.pack(pady=10)

    # Register global hotkeys
    print("\n" + "="*60)
    print("DELTA FORCE TOOL - OCR FLOAT DETECTION")
    print("="*60)

    import threading
    import ctypes
    is_admin = False
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        pass

    if not is_admin:
        print("\n⚠️  WARNING: Not running as Administrator!")
        print("   Global hotkeys will NOT work in other applications (like games).")
        print("   Please restart this program as Administrator for full functionality.")
        print()
        print("📋 How to run as Administrator:")
        print("   1. Close this terminal/window")
        print("   2. Right-click on PowerShell/Command Prompt")
        print("   3. Select 'Run as administrator'")
        print("   4. Navigate to project folder: cd 'D:\\app\\game\\DeltaForceTool'")
        print("   5. Run: uv run main.py")
        print()
        print("📝 Or create a batch file 'run_admin.bat' with this content:")
        print("   @echo off")
        print("   cd /d \"%~dp0\"")
        print("   powershell -Command \"Start-Process cmd -ArgumentList '/c cd /d \"%CD%\" && uv run main.py' -Verb RunAs\"")
        print()

    def on_exit_pressed():
        print("Exit hotkey pressed!")
        if not exit_state[0]:
            exit_state[0] = True
            main_window.destroy()

    def on_ocr_pressed():
        """Handle OCR hotkey - schedule OCR overlay creation on main thread."""
        print("OCR tool triggered!")
        # Use after() to schedule OCR creation on main thread
        main_window.after(0, launch_ocr_overlay)

    def launch_ocr_overlay():
        """Create and show the OCR overlay using main_window as the root."""
        # Use the existing main_window as root to share the Tcl interpreter
        ocr = OCRTool()
        ocr.run_as_overlay(main_window)

    def on_input_received(user_input: str) -> None:
        """Handle user input in terminal for mean calculation."""
        user_input = user_input.strip().lower()
        if user_input == 'q':
            print("Received quit command")
            input_thread_stopped[0] = True
            on_exit_pressed()
            return

        # Try to parse as integer for mean calculation
        try:
            n = int(user_input)
            if n > 0:
                print_mean(n)
            else:
                print("Please enter a positive number")
        except ValueError:
            if user_input:  # Only if not empty
                print(f"Unknown command: '{user_input}'. Enter a number to calculate mean, or 'q' to quit.")

    try:
        keyboard.add_hotkey(ocr_key, on_ocr_pressed)
        hotkey_ocr_registered = True
        if not is_admin:
            print(f"⚠️  OCR hotkey '{ocr_key}' registered (only works in this window)")
        else:
            print(f"✓ OCR hotkey '{ocr_key}' registered successfully")
    except Exception as e:
        print(f"✗ FAILED: Could not register OCR hotkey '{ocr_key}': {e}")

    try:
        keyboard.add_hotkey(exit_key, on_exit_pressed)
        hotkey_exit_registered = True
        if not is_admin:
            print(f"⚠️  Exit hotkey '{exit_key}' registered (only works in this window)")
        else:
            print(f"✓ Exit hotkey '{exit_key}' registered successfully")
    except Exception as e:
        print(f"✗ FAILED: Could not register exit hotkey '{exit_key}': {e}")

    print("\n" + "-"*60)
    print("STATUS:")
    print(f"  OCR Hotkey: {ocr_key.upper()} [{'✓' if hotkey_ocr_registered else '✗'}]")
    print(f"  Exit Hotkey: {exit_key.upper()} [{'✓' if hotkey_exit_registered else '✗'}]")
    print(f"  Admin Mode: [{'✓' if is_admin else '✗'}]")
    print("-"*60)

    if is_admin and hotkey_ocr_registered:
        status.config(text="Status: Global hotkeys active", fg="green")
    elif hotkey_ocr_registered:
        status.config(text="Status: Hotkey active (local only)", fg="yellow")
    else:
        status.config(text="Status: Hotkey failed (Run as Admin?)", fg="red")

    # Add a menu for manual exit
    menubar = tk.Menu(main_window)
    main_window.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=on_exit_pressed)
    menubar.add_cascade(label="File", menu=file_menu)

    # Start input listener thread
    def input_listener():
        """Listen for user input in terminal."""
        print("\nType a number to calculate mean of last n values, or 'q' to quit:")
        while not input_thread_stopped[0]:
            try:
                user_input = input().strip()
                if user_input:
                    main_window.after(0, on_input_received, user_input)
            except EOFError:
                break
        print("Input listener stopped")

    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()

    # Keep window alive
    main_window.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "clock":
            run_clock_only()
        elif mode == "app":
            run_main_app_with_ocr_shortcut()
        else:
            print(f"Unknown mode: {mode}. Use 'clock' or 'app'.")
            sys.exit(1)
    else:
        run_main_app_with_ocr_shortcut()
