"""Command-line entry points for DeltaForceTool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from deltaforcetool.automation import (
  PyAutoGuiInputAdapter,
  PyAutoGuiMatchAdapter,
  TesseractOCRAdapter,
  WorkflowEngine,
  WorkflowRuntimeContext,
  WorkflowStore,
  interactive_record_workflow,
)
from deltaforcetool.app.workflow import DeltaForceApp
from deltaforcetool.core.paths import get_project_paths
from deltaforcetool.tools.wegame.launcher import run_wegame_flow
from deltaforcetool.utils.time import TimeClockUI, TimeConfig
def run_clock_only() -> None:
  """Run only the time clock UI."""
  config = TimeConfig(timezone="Asia/Shanghai", update_interval_ms=100)
  clock_ui = TimeClockUI(config)
  clock_ui.create_ui()
def run_game_assist_app() -> None:
  """Run the hotkey-driven game assist application."""
  DeltaForceApp().run()
def run_workflow_file(workflow_file: str) -> None:
  """Run workflow from an explicit JSON file path."""
  store = WorkflowStore()
  definition = store.load_from_path(Path(workflow_file))
  engine = WorkflowEngine(
    input_adapter=PyAutoGuiInputAdapter(),
    ocr_adapter=TesseractOCRAdapter(),
    match_adapter=PyAutoGuiMatchAdapter(),
  )
  result = engine.execute(definition, WorkflowRuntimeContext())
  print(f"Workflow success: {result.success}, message: {result.message}")
  if not result.success:
    raise RuntimeError(result.message)
def build_parser() -> argparse.ArgumentParser:
  """Build CLI parser for runtime modes and workflow commands."""
  parser = argparse.ArgumentParser(prog="deltaforcetool")
  parser.add_argument("mode", nargs="?", default="app")
  parser.add_argument("path_or_workflow", nargs="?")
  parser.add_argument("extra", nargs="*")

  subparsers = parser.add_subparsers(dest="command")

  subparsers.add_parser("app", help="Run app mode")
  subparsers.add_parser("clock", help="Run clock mode")

  run_parser = subparsers.add_parser("workflow-run", help="Run workflow from json")
  run_parser.add_argument("workflow_file")

  record_parser = subparsers.add_parser("workflow-record", help="Record workflow interactively")
  record_parser.add_argument("workflow_id")
  record_parser.add_argument("--name", default=None)

  wegame = subparsers.add_parser("wegame", help="Launch WeGame and run automation workflow")
  wegame.add_argument("wegame_path")
  wegame.add_argument("--workflow", default=None)
  wegame.add_argument("--account", default="")
  wegame.add_argument("--password", default="")

  return parser
def _looks_like_exe_path(value: str | None) -> bool:
  if not value:
    return False
  text = value.lower()
  return text.endswith(".exe") or "\\" in value or "/" in value
def main(argv: list[str] | None = None) -> None:
  """Dispatch the requested runtime mode."""
  raw_args = list(sys.argv[1:] if argv is None else argv)
  if not raw_args:
    run_game_assist_app()
    return

  # Requirement: first argument can be WeGame path.
  if _looks_like_exe_path(raw_args[0]):
    run_wegame_flow(raw_args[0])
    return

  parser = build_parser()
  known = {"app", "clock", "workflow-run", "workflow-record", "wegame"}
  if raw_args[0] in known:
    ns = parser.parse_args(raw_args)
    if ns.command == "app":
      run_game_assist_app()
      return
    if ns.command == "clock":
      run_clock_only()
      return
    if ns.command == "workflow-run":
      run_workflow_file(ns.workflow_file)
      return
    if ns.command == "workflow-record":
      output = interactive_record_workflow(ns.workflow_id, ns.name)
      print(f"Workflow saved: {output}")
      return
    if ns.command == "wegame":
      run_wegame_flow(
        wegame_path=ns.wegame_path,
        workflow_file=ns.workflow,
        account=ns.account,
        password=ns.password,
      )
      return

  mode = raw_args[0].lower()
  if mode == "clock":
    run_clock_only()
  elif mode == "app":
    run_game_assist_app()
  elif mode == "workflow":
    paths = get_project_paths()
    print(f"Workflow directory: {paths.inst}")
  else:
    print("Unknown mode: {mode}. Use 'clock' or 'app'.".format(mode=mode))
    raise SystemExit(1)
