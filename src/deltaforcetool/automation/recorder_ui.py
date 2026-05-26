"""Interactive GUI recorder that captures clicks and simple actions into a workflow."""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import simpledialog
from pathlib import Path
from typing import List

from deltaforcetool.automation.models import Rect, WorkflowDefinition, WorkflowStep
from deltaforcetool.automation.persistence import WorkflowStore
from deltaforcetool.core.paths import get_project_paths
from PIL import ImageGrab
class RecorderUI:
  """A simple recorder overlay. Usage:
  - Drag to select an anchor region.
  - Left-click inside to record click steps.
  - Press 't' to record typing at last click position (prompts for text).
  - Press 's' to save workflow (prompts id/name).
  - Press 'Esc' to cancel.
  """
  def __init__(self) -> None:
    self._root: tk.Tk | None = None
    self._canvas: tk.Canvas | None = None
    self._screenshot_path = get_project_paths().tmp / "recorder_screenshot.png"
    self._anchor: Rect | None = None
    self._selection_rect = None
    self._selection_start = None
    self._steps: List[WorkflowStep] = []
    self._last_click = (0, 0)

  def run(self) -> None:
    self._root = tk.Tk()
    self._root.attributes("-fullscreen", True)
    self._root.attributes("-topmost", True)
    self._root.overrideredirect(True)
    self._root.configure(bg="#000000")

    # Capture screenshot for visual feedback
    try:
      img = ImageGrab.grab()
      self._screenshot_path.parent.mkdir(parents=True, exist_ok=True)
      img.save(str(self._screenshot_path))
    except Exception:
      # proceed without screenshot
      self._screenshot_path = None # type: ignore

    screen_w = self._root.winfo_screenwidth()
    screen_h = self._root.winfo_screenheight()
    self._canvas = tk.Canvas(self._root, width=screen_w, height=screen_h, highlightthickness=0)
    self._canvas.place(x=0, y=0)

    if self._screenshot_path:
      try:
        img = tk.PhotoImage(file=str(self._screenshot_path))
        self._canvas.create_image(0, 0, anchor=tk.NW, image=img)
        # keep reference
        self._canvas.image = img
      except Exception:
        pass

    self._canvas.bind('<Button-1>', self._on_mouse_down)
    self._canvas.bind('<B1-Motion>', self._on_mouse_motion)
    self._canvas.bind('<ButtonRelease-1>', self._on_mouse_release)
    self._canvas.bind('<Button-3>', self._on_right_click)
    self._root.bind('<Key>', self._on_key_press)

    instr = ("Recorder: Drag to select anchor.\n"
             "Left-click to record clicks.\n"
             "Press 't' to type text at last click. 's' to save, Esc to cancel.")
    label = tk.Label(self._root, text=instr, bg="#333333", fg="#ffffff", font=("Consolas", 12))
    label.place(x=10, y=10)

    self._root.mainloop()

  def _on_mouse_down(self, event: tk.Event) -> None:
    if self._anchor is None:
      self._selection_start = (event.x, event.y)
      self._selection_rect = self._canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=2)
    else:
      # record click step relative to anchor
      left, top = self._anchor.left, self._anchor.top
      rel_x = event.x - left
      rel_y = event.y - top
      self._last_click = (rel_x, rel_y)
      step = WorkflowStep(id=f"s{len(self._steps)+1}", action="click", params={"x": rel_x, "y": rel_y, "relative": True, "button": "left"})
      self._steps.append(step)
      # visual mark
      r = 6
      self._canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, outline='yellow', width=2)

  def _on_mouse_motion(self, event: tk.Event) -> None:
    if self._selection_rect is not None and self._selection_start is not None:
      x1, y1 = self._selection_start
      x2, y2 = event.x, event.y
      self._canvas.coords(self._selection_rect, x1, y1, x2, y2)

  def _on_mouse_release(self, event: tk.Event) -> None:
    if self._anchor is None and self._selection_rect is not None and self._selection_start is not None:
      x1, y1 = self._selection_start
      x2, y2 = event.x, event.y
      left = min(x1, x2)
      top = min(y1, y2)
      width = abs(x2 - x1)
      height = abs(y2 - y1)
      if width < 10 or height < 10:
        # ignore small
        self._canvas.delete(self._selection_rect)
        self._selection_rect = None
        self._selection_start = None
        return

      self._anchor = Rect(left=left, top=top, width=width, height=height)
      # draw anchor box thicker
      self._canvas.delete(self._selection_rect)
      self._selection_rect = self._canvas.create_rectangle(left, top, left + width, top + height, outline='cyan', width=3)
      self._canvas.create_text(left + 10, top + 10, anchor=tk.NW, text="Anchor", fill='cyan', font=("Consolas", 10))
      self._selection_start = None

  def _on_right_click(self, event: tk.Event) -> None:
    # right click saves current steps as a workflow prompt
    self._save_workflow_interactive()

  def _on_key_press(self, event: tk.Event) -> None:
    key = event.keysym.lower()
    if key == 'escape':
      self._root.destroy()
      return
    if key == 't':
      # prompt for text, create type_text step at last click
      if self._last_click is None:
        return
      text = simpledialog.askstring("Type Text", "Text to type:", parent=self._root)
      if text is None:
        return
      x, y = self._last_click
      step = WorkflowStep(id=f"s{len(self._steps)+1}", action="type_text", params={"value": text})
      self._steps.append(step)
      self._canvas.create_text(self._anchor.left + x + 10, self._anchor.top + y + 10, text=text, fill='lime', font=("Consolas", 9))
    if key == 's':
      self._save_workflow_interactive()

  def _save_workflow_interactive(self) -> None:
    if not self._steps or self._anchor is None:
      tk.messagebox.showerror("Recorder", "No anchor or steps to save.", parent=self._root)
      return
    wf_id = simpledialog.askstring("Workflow ID", "Enter workflow id:", parent=self._root)
    if not wf_id:
      return
    name = simpledialog.askstring("Workflow Name", "Enter name (optional):", parent=self._root) or wf_id

    workflow = WorkflowDefinition(
      workflow_id=wf_id,
      name=name,
      anchor=self._anchor,
      steps=self._steps,
      start_step=self._steps[0].id,
    )
    store = WorkflowStore()
    target = store.save(workflow)
    tk.messagebox.showinfo("Recorder", f"Saved workflow: {target}", parent=self._root)
    self._root.destroy()
def launch_recorder_overlay() -> str:
  ui = RecorderUI()
  ui.run()
  return "ok"
