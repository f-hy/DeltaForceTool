# src/deltaforcetool/conf/global_hotkey.py
"""Global hotkey implementation using keyboard library."""

import threading
import tkinter as tk
from typing import Callable, Optional


class GlobalHotkeyManager:
    """Manage global hotkeys using keyboard library."""

    def __init__(self):
        self._root: Optional[tk.Tk] = None
        self._hotkeys: dict[str, Callable] = {}
        self._polling = False
        self._poll_thread: Optional[threading.Thread] = None

    def register(self, key: str, callback: Callable) -> bool:
        """Register a global hotkey.

        Args:
            key: Hotkey combination like 'alt+s', 'ctrl+alt+q'
            callback: Function to call when hotkey is pressed

        Returns:
            True if registration successful, False otherwise
        """
        import keyboard

        def wrapper():
            try:
                callback()
            except Exception as e:
                print(f"Error in hotkey callback: {e}")

        try:
            keyboard.add_hotkey(key, wrapper)
            self._hotkeys[key] = callback
            return True
        except Exception as e:
            print(f"Failed to register hotkey '{key}': {e}")
            return False

    def start(self):
        """Start the hotkey polling thread."""
        if self._poll_thread is None or not self._poll_thread.is_alive():
            self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._poll_thread.start()

    def _poll_loop(self):
        """Poll for hotkey presses."""
        import time
        while True:
            time.sleep(0.01)  # 10ms polling interval
