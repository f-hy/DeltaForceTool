"""Runtime adapter protocols and default implementations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import sleep, time
from typing import Protocol

from PIL import ImageGrab
import pytesseract

from deltaforcetool.core.paths import get_project_paths
from deltaforcetool.tools.ocr.float_detector import FloatDetector
class InputAdapter(Protocol):
  """Input actions needed by the workflow engine."""
  def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
    """Click at a screen position."""

  def press(self, key: str) -> None:
    """Press a keyboard key."""

  def type_text(self, value: str) -> None:
    """Type text using keyboard automation."""
class MatchAdapter(Protocol):
  """Image match adapter for screen templates."""
  def locate(self, template_path: Path, region: tuple[int, int, int, int] | None = None) -> tuple[int, int] | None:
    """Return center point if template was located."""
class OCRAdapter(Protocol):
  """OCR adapter for reading region text."""
  def read_text(self, region: tuple[int, int, int, int]) -> str:
    """Read text from region."""
@dataclass
class WorkflowRuntimeContext:
  """Mutable runtime context for a workflow execution."""

  variables: dict[str, str] = field(default_factory=dict)
  logs: list[str] = field(default_factory=list)

  def log(self, message: str) -> None:
    self.logs.append(message)
class PyAutoGuiInputAdapter:
  """pyautogui-based input adapter."""
  def __init__(self) -> None:
    import pyautogui

    self._pyautogui = pyautogui

  def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
    self._pyautogui.click(x=x, y=y, button=button, clicks=clicks)

  def press(self, key: str) -> None:
    self._pyautogui.press(key)

  def type_text(self, value: str) -> None:
    self._pyautogui.write(value)
class PyAutoGuiMatchAdapter:
  """pyautogui locate-based matcher."""
  def __init__(self) -> None:
    import pyautogui

    self._pyautogui = pyautogui

  def locate(self, template_path: Path, region: tuple[int, int, int, int] | None = None) -> tuple[int, int] | None:
    location = self._pyautogui.locateCenterOnScreen(str(template_path), region=region)
    if location is None:
      return None
    return int(location.x), int(location.y)
class TesseractOCRAdapter:
  """OCR adapter using screenshot crop + tesseract."""
  def __init__(self) -> None:
    self._detector = FloatDetector(model_dir=get_project_paths().models)

  def read_text(self, region: tuple[int, int, int, int]) -> str:
    left, top, width, height = region
    image = ImageGrab.grab(bbox=(left, top, left + width, top + height))
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()
def now_ms() -> int:
  """Return monotonic-like timestamp in milliseconds."""
  return int(time() * 1000)
def sleep_ms(milliseconds: int) -> None:
  """Sleep for milliseconds."""
  if milliseconds > 0:
    sleep(milliseconds / 1000.0)
