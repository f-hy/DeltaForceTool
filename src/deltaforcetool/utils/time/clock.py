# src/deltaforcetool/utils/time/clock.py
import tkinter as tk
from datetime import datetime, timezone, timedelta
from typing import Optional

from .singleton import Singleton
from .observer import Subject, Observer, TimeEvent
from .models import TimeConfig, TimeEvent as TimeEventData


class TimeClock(Singleton, Subject):
    """Singleton TimeClock that notifies observers of time updates."""

    _instance: "TimeClock | None" = None
    _timer_id: Optional[int] = None

    def __init__(self, config: Optional[TimeConfig] = None) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._config = config or TimeConfig()
        self._observers: list[Observer] = []
        self._initialized = True
        self._running = False
        self._root: Optional[tk.Tk] = None

    @classmethod
    def instance(cls, config: Optional[TimeConfig] = None) -> "TimeClock":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(config)
        return cls._instance  # type: ignore

    def subscribe(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: TimeEvent) -> None:
        for observer in self._observers:
            observer.update(event)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        if self._root is None:
            self._root = tk.Tk()
            self._root.overrideredirect(True)
            self._root.attributes("-topmost", True)
            transparent_color = "#010203"
            self._root.configure(bg=transparent_color)
            self._root.attributes("-transparentcolor", transparent_color)
        self._update()

    def stop(self) -> None:
        self._running = False
        if self._timer_id:
            self._root.after_cancel(self._timer_id)  # type: ignore
            self._timer_id = None

    def _update(self) -> None:
        if not self._running:
            return

        tz_offset = timezone(timedelta(hours=8))  # Beijing timezone UTC+8
        now = datetime.now(tz_offset)

        # Format: HH:MM:S.m (保留 1 位毫秒，e.g., 12:34:56.7)
        time_str = now.strftime("%H:%M:%S.") + f"{now.microsecond // 100000:01d}"

        event = TimeEventData(
            timestamp=now.timestamp(),
            current_time=now,
            formatted_time=time_str,
            timezone=self._config.timezone
        )
        self.notify(event)

        self._timer_id = self._root.after(self._config.update_interval_ms, self._update)  # type: ignore


class TkinterTimeDisplay(Observer):
    """Tkinter-based time display implementation."""

    def __init__(self, clock: TimeClock) -> None:
        self.clock = clock
        self.transparent_color = "#010203"
        self.label: Optional[tk.Label] = None
        self.x: Optional[int] = None
        self.y: Optional[int] = None
        self.root: Optional[tk.Tk] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.root = self.clock._root
        if self.root is None:
            self.root = tk.Tk()
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.configure(bg=self.transparent_color)
            self.root.attributes("-transparentcolor", self.transparent_color)
            self.clock._root = self.root
        self.label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 32, "bold"),
            fg="#00ff00",
            bg=self.transparent_color
        )
        self.label.pack(padx=15, pady=10)

    def update(self, event: TimeEvent) -> None:
        if self.label:
            self.label.config(text=event.formatted_time)

    def start_drag(self, event: tk.Event) -> None:
        self.x = event.x
        self.y = event.y

    def stop_drag(self, event: tk.Event) -> None:
        self.x = None
        self.y = None

    def do_drag(self, event: tk.Event) -> None:
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")


class TimeClockUI:
    """Convenience class for creating a draggable clock UI."""

    def __init__(self, config: Optional[TimeConfig] = None):
        self.clock = TimeClock.instance(config)
        self.display: Optional[TkinterTimeDisplay] = None

    def create_ui(self) -> None:
        # Start clock first to create the root window
        self.clock.start()
        # Then create the display which will use the existing root
        self.display = TkinterTimeDisplay(self.clock)
        self.display.root.bind("<ButtonPress-1>", self.display.start_drag)
        self.display.root.bind("<ButtonRelease-1>", self.display.stop_drag)
        self.display.root.bind("<B1-Motion>", self.display.do_drag)

        menu = tk.Menu(self.display.root, tearoff=0)
        menu.add_command(label="关闭程序", command=lambda: self.stop())
        self.display.root.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

        self.clock.subscribe(self.display)
        # Start the main event loop - this blocks and keeps the window alive
        self.display.root.mainloop()

    def stop(self) -> None:
        self.clock.stop()
        if self.display:
            self.display.root.destroy()
