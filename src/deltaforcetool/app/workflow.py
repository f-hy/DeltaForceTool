"""Application workflow orchestration."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Protocol

import tkinter as tk
from tkinter import filedialog

from deltaforcetool.core.settings import AppSettings, load_app_settings
from deltaforcetool.infrastructure.hotkeys import GlobalHotkeyManager
from deltaforcetool.tools.mean.mean_tool import MeanTool
from deltaforcetool.tools.ocr.ocr_tool import OCRTool
class Notifier(Protocol):
  """Notification sink for workflow feedback."""
  def info(self, message: str) -> None:
    """Report an informational message."""

  def warning(self, message: str) -> None:
    """Report a warning message."""

  def error(self, message: str) -> None:
    """Report an error message."""
@dataclass
class ConsoleNotifier:
  """Simple console notifier used by the default workflow."""
  def info(self, message: str) -> None:
    print(message)

  def warning(self, message: str) -> None:
    print(f"WARNING: {message}")

  def error(self, message: str) -> None:
    print(f"ERROR: {message}")
class DeltaForceApp:
  """Main application controller for hotkey-driven workflows."""
  def __init__(
    self,
    settings: AppSettings | None = None,
    notifier: Notifier | None = None,
    hotkeys: GlobalHotkeyManager | None = None,
  ) -> None:
    self.settings = settings or load_app_settings()
    self.notifier = notifier or ConsoleNotifier()
    self.hotkeys = hotkeys or GlobalHotkeyManager()
    self._root: tk.Tk | None = None
    self._shutdown_requested = False

  @staticmethod
  def _is_admin() -> bool:
    """Return whether the current process is elevated on Windows."""
    try:
      return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
      return False

  def run(self) -> None:
    """Start the UI and hotkey loop."""
    self._root = tk.Tk()
    self._root.title("DeltaForceTool")
    self._root.geometry("260x140")
    self._root.attributes("-topmost", True)

    self._build_ui(self._root)
    self._register_hotkeys()
    self._root.protocol("WM_DELETE_WINDOW", self.request_exit)

    self.notifier.info("DeltaForceTool started")
    self._root.mainloop()

  def _build_ui(self, root: tk.Tk) -> None:
    title = tk.Label(root, text="DeltaForceTool", font=("Consolas", 12, "bold"))
    title.pack(pady=(12, 4))

    hotkey_label = tk.Label(
      root,
      text=(f"OCR: {self.settings.hotkeys.ocr_trigger.upper()}\n"
            f"Mean: {self.settings.hotkeys.mean_calculate.upper()}\n"
            f"Record: {self.settings.hotkeys.workflow_record.upper()}\n"
            f"Run: {self.settings.hotkeys.workflow_run.upper()}"),
      font=("Consolas", 10),
    )
    hotkey_label.pack()

    status_text = "Administrator mode active" if self._is_admin() else "Run as administrator for global hotkeys"
    status = tk.Label(root, text=status_text, font=("Consolas", 8), fg="gray")
    status.pack(pady=(8, 10))

    footer = tk.Label(root, text="File > Exit or Ctrl+Alt+Q", font=("Consolas", 8), fg="gray")
    footer.pack()

  def _register_hotkeys(self) -> None:
    ocr_registered = self.hotkeys.register(self.settings.hotkeys.ocr_trigger, self.request_ocr)
    mean_registered = self.hotkeys.register(self.settings.hotkeys.mean_calculate, self.request_mean)
    record_registered = self.hotkeys.register(self.settings.hotkeys.workflow_record, self.request_record_workflow)
    run_registered = self.hotkeys.register(self.settings.hotkeys.workflow_run, self.request_run_workflow)
    exit_registered = self.hotkeys.register(self.settings.hotkeys.exit, self.request_exit)

    if not ocr_registered:
      self.notifier.warning(f"OCR hotkey '{self.settings.hotkeys.ocr_trigger}' could not be registered")
    if not mean_registered:
      self.notifier.warning(f"Mean hotkey '{self.settings.hotkeys.mean_calculate}' could not be registered")
    if not record_registered:
      self.notifier.warning(f"Record hotkey '{self.settings.hotkeys.workflow_record}' could not be registered")
    if not run_registered:
      self.notifier.warning(f"Run hotkey '{self.settings.hotkeys.workflow_run}' could not be registered")
    if not exit_registered:
      self.notifier.warning(f"Exit hotkey '{self.settings.hotkeys.exit}' could not be registered")

  def request_ocr(self) -> None:
    """Schedule the OCR overlay on the Tk thread."""
    if self._root is None:
      return
    self._root.after(0, self._launch_ocr_overlay)

  def _launch_ocr_overlay(self) -> None:
    """Create and show the OCR overlay."""
    if self._root is None:
      return

    self.notifier.info("OCR workflow triggered")
    OCRTool().run_as_overlay(self._root)

  def request_mean(self) -> None:
    """Schedule mean calculation prompt on Tk thread."""
    if self._root is None:
      return
    self._root.after(0, self._launch_mean_dialog)

  def _launch_mean_dialog(self) -> None:
    """Prompt for x and show latest OCR mean result."""
    self.notifier.info("Mean calculation triggered")
    MeanTool().run()

  def request_record_workflow(self) -> None:
    """Launch GUI recorder overlay on the Tk thread."""
    if self._root is None:
      return

    def _launch():
      try:
        from deltaforcetool.automation import launch_recorder_overlay

        launch_recorder_overlay()
        self.notifier.info("Recorder finished")
      except Exception as exc:
        self.notifier.error(f"Recorder failed: {exc}")

    self._root.after(0, _launch)

  def request_run_workflow(self) -> None:
    """Prompt for a workflow file and run it once."""
    if self._root is None:
      return
    self._root.after(0, self._prompt_and_run_workflow)

  def _prompt_and_run_workflow(self) -> None:
    """Prompt file path and dispatch workflow execution."""
    from deltaforcetool.app.cli import run_workflow_file

    if self._root is None:
      return

    selected = filedialog.askopenfilename(
      title="Select workflow JSON",
      filetypes=[("Workflow JSON", "*.json"), ("All files", "*.*")],
    )
    if not selected:
      return

    try:
      run_workflow_file(selected)
      self.notifier.info(f"Workflow finished: {selected}")
    except Exception as exc:
      self.notifier.error(f"Workflow failed: {exc}")

  def request_exit(self) -> None:
    """Schedule a safe shutdown on the Tk thread."""
    if self._root is None or self._shutdown_requested:
      return
    self._shutdown_requested = True
    self._root.after(0, self.shutdown)

  def shutdown(self) -> None:
    """Shut down the app and clear hotkeys."""
    self.hotkeys.clear()
    if self._root is not None:
      try:
        self._root.destroy()
      except tk.TclError:
        pass
      self._root = None
