# src/deltaforcetool/tools/ocr/ocr_tool.py
"""OCR Tool implementation with Tkinter overlay UI."""

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
  import tkinter as tk

from PIL import ImageGrab

from deltaforcetool.core.base import ITool
from deltaforcetool.tools.ocr.float_detector import FloatDetector
class OCRTool(ITool):
  """OCR tool for float number detection with rectangle selection.

    This tool captures a screenshot, shows it in a fullscreen Tkinter overlay,
    allows the user to select a rectangle region, and performs OCR on that region.
    """

  name = "ocr"
  _instance: Optional["OCRTool"] = None

  def __new__(cls):
    """Ensure only one instance exists at a time."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self):
    """Initialize the OCR tool."""
    if hasattr(self, '_initialized') and self._initialized:
      return
    self._initialized = True
    self._running = False
    self._detector = FloatDetector()
    # Get project root
    project_root = Path(__file__).resolve().parents[4]
    self._screenshot_path = project_root / "data" / "tmp" / "freeze_temp.png"
    self._output_file = project_root / "data" / "ocr.out"
    self._parent_root = None # Parent Tk root window

  def run(self) -> None:
    """Start the OCR tool - capture screenshot and show overlay UI.

        NOTE: Creates its own Tk root. Use run_as_overlay() for integration
        with existing main window.
        """
    self._running = True
    OCRTool._instance = self

    # Capture screenshot
    try:
      self._screenshot = ImageGrab.grab()
    except Exception as e:
      print(f"Failed to capture screen: {e}")
      self.stop()
      return

    # Create overlay window
    import tkinter as tk
    self._freeze_overlay = tk.Tk()
    self._freeze_overlay.attributes('-fullscreen', True)
    self._freeze_overlay.attributes('-topmost', True)
    self._freeze_overlay.configure(bg='#000000')
    self._freeze_overlay.overrideredirect(True)
    self._freeze_overlay.attributes('-alpha', 0.7)

    self._show_freeze_overlay()

  def run_as_overlay(self, parent_root: 'tk.Tk') -> None:
    """Start the OCR tool as an overlay on the parent root window.

        This method uses the provided parent root to share the Tcl interpreter,
        avoiding thread/s apartment issues with multiple Tk instances.
        """
    self._running = True
    OCRTool._instance = self
    self._parent_root = parent_root

    # Capture screenshot
    try:
      self._screenshot = ImageGrab.grab()
    except Exception as e:
      print(f"Failed to capture screen: {e}")
      self.stop()
      return

    # Create Toplevel overlay window using parent root
    import tkinter as tk
    self._freeze_overlay = tk.Toplevel(parent_root)
    self._freeze_overlay.attributes('-fullscreen', True)
    self._freeze_overlay.attributes('-topmost', True)
    self._freeze_overlay.configure(bg='#000000')
    self._freeze_overlay.overrideredirect(True)
    self._freeze_overlay.attributes('-alpha', 0.7)

    self._show_freeze_overlay()

  def stop(self) -> None:
    """Stop the OCR tool."""
    self._running = False
    if hasattr(self, '_freeze_image_ref') and self._freeze_image_ref is not None:
      self._freeze_image_ref = None
    if hasattr(self, '_freeze_overlay') and self._freeze_overlay is not None:
      try:
        self._freeze_overlay.destroy()
      except:
        pass
      self._freeze_overlay = None
    self._parent_root = None
    OCRTool._instance = None

  def _show_freeze_overlay(self) -> None:
    """Show a transparent fullscreen overlay with frozen screenshot."""
    try:
      import tkinter as tk

      # Save screenshot
      self._screenshot_path.parent.mkdir(parents=True, exist_ok=True)
      self._screenshot.save(str(self._screenshot_path))
      print(f"Screenshot saved to {self._screenshot_path}")

      # Create Canvas FIRST (on top layer) for mouse interaction
      screen_width = self._freeze_overlay.winfo_screenwidth()
      screen_height = self._freeze_overlay.winfo_screenheight()
      self._canvas = tk.Canvas(self._freeze_overlay, width=screen_width, height=screen_height, highlightthickness=0)
      self._canvas.place(x=0, y=0)

      # Load and display image on Canvas
      freeze_image = tk.PhotoImage(file=str(self._screenshot_path))
      self._freeze_image_ref = freeze_image
      self._canvas.create_image(0, 0, anchor=tk.NW, image=freeze_image)
      self._canvas.image = freeze_image

      # Make sure overlay is focused
      self._freeze_overlay.focus_force()
    except Exception as e:
      print(f"Failed to display screenshot: {e}")
      print(f"screenshot_path = {self._screenshot_path}")
      import traceback
      traceback.print_exc()
      self.stop()
      return

    # Bind mouse events on canvas (not overlay)
    self._canvas.bind('<Button-1>', self._on_mouse_down)
    self._canvas.bind('<ButtonRelease-1>', self._on_mouse_release)

    # Start mainloop
    self._freeze_overlay.mainloop()

  def _on_mouse_down(self, event: 'tk.Event') -> None:
    """Handle mouse button down - start of selection."""
    import tkinter as tk
    print(f"Mouse down at: ({event.x}, {event.y})")
    self._is_selecting = True
    self._selection_start = (event.x, event.y)

    # Create red rectangle at the click position (initially 0-sized)
    self._selection_rect = self._canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=3, dash=(4, 2))
    print(f"Created selection rect at ({event.x}, {event.y})")

    # Bind motion to canvas - events will come to canvas
    self._canvas.bind('<B1-Motion>', self._on_mouse_motion)

  def _on_mouse_motion(self, event: 'tk.Event') -> None:
    """Handle mouse motion while dragging - update selection rectangle."""
    if self._is_selecting and self._selection_rect is not None and self._selection_start is not None:
      x1, y1 = self._selection_start
      x2, y2 = event.x, event.y
      self._canvas.coords(self._selection_rect, x1, y1, x2, y2)

  def _on_mouse_release(self, event: 'tk.Event') -> None:
    """Handle mouse button release - end of selection and perform OCR."""
    print(f"Mouse release at: ({event.x}, {event.y})")
    self._is_selecting = False

    if self._selection_rect is None or self._selection_start is None:
      print("No selection rect or start, aborting")
      self._cleanup_selection()
      self.stop()
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

    print(f"Selection: left={left}, top={top}, right={right}, bottom={bottom}")
    print(f"Size: {width}x{height}")

    if width < 10 or height < 10:
      print("Selection too small, aborting")
      self._cleanup_selection()
      self.stop()
      return

    # Save selected region screenshot for testing
    try:
      if hasattr(self, '_screenshot') and self._screenshot:
        selected_screenshot_path = self._screenshot_path.parent / "selected_region.png"
        region_for_display = self._screenshot.crop((left, top, right, bottom))
        region_for_display.save(str(selected_screenshot_path))
        print(f"Selected region screenshot saved to {selected_screenshot_path}")
    except Exception as e:
      print(f"Failed to save selected region screenshot: {e}")

    # Extract region and perform OCR
    try:
      if hasattr(self, '_screenshot') and self._screenshot:
        region_image = self._screenshot.crop((left, top, right, bottom))
        # Pass (0, 0, width, height) since region_image is already cropped
        results = self._detector.detect_and_save(region_image, (0, 0, width, height))
        print(f"Detected {len(results)} float numbers, saved to {self._detector.output_file}")
      else:
        print("No screenshot available")
    except Exception as e:
      print(f"OCR error: {e}")

    self._cleanup_selection()
    self.stop()

  def _cleanup_selection(self) -> None:
    """Clean up selection UI elements."""
    print("Cleaning up selection...")
    # Delete the selection rectangle
    if hasattr(self, '_selection_rect') and self._selection_rect is not None:
      try:
        self._canvas.delete(self._selection_rect)
        print(f"Deleted selection rect: {self._selection_rect}")
      except:
        pass
      self._selection_rect = None
    self._selection_start = None
    self._is_selecting = False
