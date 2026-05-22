# src/deltaforcetool/tools/ocr/ocr_tool.py
"""OCR Tool implementation with Tkinter overlay UI."""

import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple

from PIL import ImageGrab

from deltaforcetool.core.base import ITool
from deltaforcetool.tools.ocr.float_detector import FloatDetector


class OCRTool(ITool):
    """OCR tool for float number detection with rectangle selection."""

    name = "ocr"

    def __init__(self):
        """Initialize the OCR tool."""
        self._running = False
        self._detector = FloatDetector()
        self._root: Optional[tk.Tk] = None
        self._canvas: Optional[tk.Canvas] = None
        self._selection_start: Optional[Tuple[int, int]] = None
        self._selection_rect: Optional[int] = None
        self._freeze_overlay: Optional[tk.Toplevel] = None
        self._freeze_label: Optional[tk.Label] = None

    def run(self) -> None:
        """Start the OCR tool."""
        self._running = True
        self._show_freeze_overlay()

    def stop(self) -> None:
        """Stop the OCR tool."""
        self._running = False
        if self._root:
            self._root.destroy()
        if self._freeze_overlay:
            self._freeze_overlay.destroy()

    def _show_freeze_overlay(self) -> None:
        """Show a semi-transparent overlay to freeze the screen."""
        self._freeze_overlay = tk.Toplevel()
        self._freeze_overlay.attributes('-fullscreen', True)
        self._freeze_overlay.attributes('-topmost', True)
        self._freeze_overlay.configure(bg='black')
        self._freeze_overlay.overrideredirect(True)

        # Capture current screen
        try:
            screenshot = ImageGrab.grab()
            screenshot_path = Path(__file__).parent.parent.parent / "data" / "freeze_temp.png"
            screenshot.save(str(screenshot_path))
            freeze_image = tk.PhotoImage(file=screenshot_path)

            self._freeze_label = tk.Label(self._freeze_overlay, image=freeze_image)
            self._freeze_label.pack()
            self._freeze_label.image = freeze_image  # Keep reference
        except Exception:
            # Fallback to solid overlay if screenshot fails
            self._freeze_label = tk.Label(self._freeze_overlay, bg='gray')
            self._freeze_label.pack()

        # Bind left click to start rectangle selection
        self._freeze_overlay.bind('<Button-1>', self._on_mouse_down)

    def _on_mouse_down(self, event: tk.Event) -> None:
        """Handle mouse button down for rectangle selection start."""
        self._selection_start = (event.x, event.y)
        self._canvas = tk.Canvas(self._freeze_overlay)
        self._canvas.place(x=0, y=0, width=event.winfo_screenwidth(), height=event.winfo_screenheight())

        self._selection_rect = self._canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline='red', width=2
        )
        self._freeze_overlay.bind('<B1-Motion>', self._on_mouse_motion)
        self._freeze_overlay.bind('<ButtonRelease-1>', self._on_mouse_release)

    def _on_mouse_motion(self, event: tk.Event) -> None:
        """Handle mouse motion for rectangle selection update."""
        if self._selection_rect is not None and self._selection_start is not None:
            x1, y1 = self._selection_start
            x2, y2 = event.x, event.y
            self._canvas.coords(self._selection_rect, x1, y1, x2, y2)

    def _on_mouse_release(self, event: tk.Event) -> None:
        """Handle mouse button release to perform OCR on selected region."""
        if self._selection_rect is None or self._selection_start is None:
            return

        x1, y1 = self._selection_start
        x2, y2 = event.x, event.y

        # Normalize coordinates
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top

        if width < 10 or height < 10:
            # Selection too small, ignore
            self._cleanup_selection()
            return

        # Capture the selected region
        try:
            region_image = ImageGrab.grab(bbox=(left, top, right, bottom))
            results = self._detector.detect_and_save(region_image, (left, top, width, height))
            print(f"Detected {len(results)} float numbers, saved to {self._detector.output_file}")
        except Exception as e:
            print(f"OCR error: {e}")

        self._cleanup_selection()

    def _cleanup_selection(self) -> None:
        """Clean up selection UI elements."""
        if self._canvas:
            self._canvas.destroy()
            self._canvas = None
        self._selection_rect = None
        self._selection_start = None

        # Stop tool after selection
        self.stop()
