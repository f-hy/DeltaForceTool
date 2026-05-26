"""Command-line entry points for DeltaForceTool."""

from __future__ import annotations

import sys

from deltaforcetool.app.workflow import DeltaForceApp
from deltaforcetool.utils.time import TimeClockUI, TimeConfig
def run_clock_only() -> None:
  """Run only the time clock UI."""
  config = TimeConfig(timezone="Asia/Shanghai", update_interval_ms=100)
  clock_ui = TimeClockUI(config)
  clock_ui.create_ui()
def run_game_assist_app() -> None:
  """Run the hotkey-driven game assist application."""
  DeltaForceApp().run()
def main(argv: list[str] | None = None) -> None:
  """Dispatch the requested runtime mode."""
  args = list(sys.argv[1:] if argv is None else argv)
  if not args:
    run_game_assist_app()
    return

  mode = args[0].lower()
  if mode == "clock":
    run_clock_only()
  elif mode == "app":
    run_game_assist_app()
  else:
    print("Unknown mode: {mode}. Use 'clock' or 'app'.".format(mode=mode))
    raise SystemExit(1)
