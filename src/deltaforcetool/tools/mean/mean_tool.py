"""Interactive mean calculation tool for OCR values."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog

from deltaforcetool.core.base import ITool
from deltaforcetool.utils.ocr import calculate_mean
class MeanTool(ITool):
  """Prompt for x and calculate mean of latest OCR values."""

  name = "mean"

  def __init__(self) -> None:
    self._dialog_root: tk.Toplevel | None = None

  def run(self) -> None:
    parent = tk._default_root
    if parent is None:
      parent = tk.Tk()
      parent.withdraw()

    answer = simpledialog.askstring("OCR Mean", "输入 x（最近 x 个值求均值）:", parent=parent)
    if answer is None:
      return

    try:
      count = int(answer.strip())
      if count <= 0:
        raise ValueError("x 必须大于 0")
      value = calculate_mean(count)
      result = f"最近 {count} 个值的均值: {value}"
      print(result)
      messagebox.showinfo("OCR Mean", result, parent=parent)
    except Exception as exc:
      message = f"计算失败: {exc}"
      print(message)
      messagebox.showerror("OCR Mean", message, parent=parent)

  def stop(self) -> None:
    """No long-running state to stop."""
    if self._dialog_root is not None:
      try:
        self._dialog_root.destroy()
      except tk.TclError:
        pass
      self._dialog_root = None
