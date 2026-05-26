"""Global hotkey helpers."""

from collections.abc import Callable
from contextlib import suppress
class GlobalHotkeyManager:
  """Register and clear keyboard hotkeys."""
  def __init__(self) -> None:
    self._registered_handles: list[object] = []

  def register(self, key: str, callback: Callable[[], None]) -> bool:
    """Register a hotkey callback."""
    try:
      import keyboard
    except ImportError as exc:
      print(f"Keyboard library not available: {exc}")
      return False

    def wrapped_callback() -> None:
      try:
        callback()
      except Exception as error:
        print(f"Error in hotkey callback for '{key}': {error}")

    try:
      handle = keyboard.add_hotkey(key, wrapped_callback)
      self._registered_handles.append(handle)
      return True
    except Exception as error:
      print(f"Failed to register hotkey '{key}': {error}")
      return False

  def clear(self) -> None:
    """Clear all registered hotkeys."""
    try:
      import keyboard
    except ImportError:
      self._registered_handles.clear()
      return

    for handle in self._registered_handles:
      with suppress(Exception):
        keyboard.remove_hotkey(handle)
    self._registered_handles.clear()
