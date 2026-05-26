"""Application settings loading."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .paths import get_project_paths
@dataclass(frozen=True)
class HotkeySettings:
  """Hotkey bindings for the application."""

  ocr_trigger: str = "alt+s"
  exit: str = "ctrl+alt+q"
@dataclass(frozen=True)
class OCRSettings:
  """OCR overlay appearance settings."""

  overlay_alpha: float = 0.7
  rect_color: str = "#00ff00"
  rect_width: int = 3
  rect_dash: tuple[int, int] = (4, 2)
@dataclass(frozen=True)
class AppSettings:
  """Top-level application settings."""

  hotkeys: HotkeySettings = field(default_factory=HotkeySettings)
  ocr: OCRSettings = field(default_factory=OCRSettings)
def load_app_settings(config_path: Path | None = None) -> AppSettings:
  """Load settings from the repository config file."""
  paths = get_project_paths()
  settings_path = config_path or paths.conf / "keymap.json"

  payload: dict[str, Any] = {}
  if settings_path.exists():
    with settings_path.open("r", encoding="utf-8") as file_handle:
      payload = json.load(file_handle)

  hotkey_data = payload.get("hotkeys", {})
  ocr_data = payload.get("ocr_settings", {})
  rect_dash = ocr_data.get("rect_dash", (4, 2))
  if isinstance(rect_dash, list):
    rect_dash = tuple(rect_dash)

  return AppSettings(
    hotkeys=HotkeySettings(
      ocr_trigger=hotkey_data.get("ocr_trigger", "alt+s"),
      exit=hotkey_data.get("exit", "ctrl+alt+q"),
    ),
    ocr=OCRSettings(
      overlay_alpha=float(ocr_data.get("overlay_alpha", 0.7)),
      rect_color=str(ocr_data.get("rect_color", "#00ff00")),
      rect_width=int(ocr_data.get("rect_width", 3)),
      rect_dash=tuple(rect_dash),
    ),
  )
