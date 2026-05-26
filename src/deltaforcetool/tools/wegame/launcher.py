"""WeGame launcher and default automation workflow."""

from __future__ import annotations

import ctypes
from pathlib import Path

from deltaforcetool.automation import (
  PyAutoGuiInputAdapter,
  PyAutoGuiMatchAdapter,
  Rect,
  TesseractOCRAdapter,
  WorkflowDefinition,
  WorkflowEngine,
  WorkflowRuntimeContext,
  WorkflowStep,
  WorkflowStore,
)
from deltaforcetool.core.paths import get_project_paths
def launch_wegame_admin(executable: str | Path) -> None:
  """Launch WeGame executable with runas (UAC prompt)."""
  path = Path(executable).expanduser().resolve()
  if not path.exists():
    raise FileNotFoundError(f"WeGame path does not exist: {path}")

  result = ctypes.windll.shell32.ShellExecuteW(
    None,
    "runas",
    str(path),
    None,
    str(path.parent),
    1,
  )
  if int(result) <= 32:
    raise RuntimeError(f"Failed to launch WeGame as admin, ShellExecuteW code={result}")
def ensure_default_wegame_workflow() -> Path:
  """Create default WeGame workflow JSON if it does not exist."""
  paths = get_project_paths()
  paths.ensure_data_dirs()
  store = WorkflowStore(paths.inst)
  workflow_id = "wegame_default"
  target = store.workflow_path(workflow_id)
  if target.exists():
    return target

  default = WorkflowDefinition(
    workflow_id=workflow_id,
    name="WeGame default launch",
    anchor=Rect(left=0, top=0, width=1920, height=1080),
    start_step="wait_login_text",
    steps=[
      WorkflowStep(
        id="wait_login_text",
        action="wait_for_text",
        params={
          "text": "登录",
          "region": {
            "left": 450,
            "top": 200,
            "width": 1000,
            "height": 600,
            "relative": True},
          "timeout_ms": 120000,
          "interval_ms": 800,
          "post_delay_ms": 500, },
        next_step="read_account",
        on_failure="wait_login_image",
      ),
      WorkflowStep(
        id="wait_login_image",
        action="image_match_click",
        params={
          "template": "login_button.png",
          "template_base": str(paths.match_materials),
          "region": {
            "left": 450,
            "top": 200,
            "width": 1000,
            "height": 600,
            "relative": True}, },
        next_step="read_account",
      ),
      WorkflowStep(
        id="read_account",
        action="ocr_text",
        params={
          "var": "account_text",
          "region": {
            "left": 530,
            "top": 310,
            "width": 360,
            "height": 60,
            "relative": True}, },
        next_step="read_password",
      ),
      WorkflowStep(
        id="read_password",
        action="ocr_text",
        params={
          "var": "password_text",
          "region": {
            "left": 530,
            "top": 390,
            "width": 360,
            "height": 60,
            "relative": True}, },
        next_step="account_ready",
      ),
      WorkflowStep(
        id="account_ready",
        action="branch_if",
        params={"condition": "not_empty:account_text"},
        on_success="password_ready",
        on_failure="fill_account",
      ),
      WorkflowStep(
        id="password_ready",
        action="branch_if",
        params={"condition": "not_empty:password_text"},
        on_success="click_login",
        on_failure="fill_password",
      ),
      WorkflowStep(
        id="fill_account",
        action="click",
        params={
          "x": 690,
          "y": 340,
          "relative": True,
          "button": "left"},
        next_step="type_account",
      ),
      WorkflowStep(
        id="type_account",
        action="type_text",
        params={"value": "{{account}}"},
        next_step="fill_password",
      ),
      WorkflowStep(
        id="fill_password",
        action="click",
        params={
          "x": 690,
          "y": 420,
          "relative": True,
          "button": "left"},
        next_step="type_password",
      ),
      WorkflowStep(
        id="type_password",
        action="type_text",
        params={"value": "{{password}}"},
        next_step="click_login",
      ),
      WorkflowStep(
        id="click_login",
        action="image_match_click",
        params={
          "template": "login_button.png",
          "template_base": str(paths.match_materials),
          "region": {
            "left": 450,
            "top": 200,
            "width": 1000,
            "height": 600,
            "relative": True}, },
        next_step="wait_home",
      ),
      WorkflowStep(
        id="wait_home",
        action="wait_ms",
        params={"ms": 8000},
        next_step="click_delta_force",
      ),
      WorkflowStep(
        id="click_delta_force",
        action="image_match_click",
        params={
          "template": "delta_force_left_tab.png",
          "template_base": str(paths.match_materials),
          "region": {
            "left": 0,
            "top": 120,
            "width": 500,
            "height": 900,
            "relative": True}, },
        next_step="click_start",
      ),
      WorkflowStep(
        id="click_start",
        action="image_match_click",
        params={
          "template": "start_button.png",
          "template_base": str(paths.match_materials),
          "region": {
            "left": 1350,
            "top": 700,
            "width": 560,
            "height": 350,
            "relative": True}, },
      ), ],
  )

  return store.save(default)
def run_wegame_flow(
  wegame_path: str,
  workflow_file: str | None = None,
  account: str | None = None,
  password: str | None = None,
) -> None:
  """Launch WeGame and execute workflow automation."""
  launch_wegame_admin(wegame_path)

  target = Path(workflow_file) if workflow_file else ensure_default_wegame_workflow()
  store = WorkflowStore()
  workflow = store.load_from_path(target)

  context = WorkflowRuntimeContext(variables={
    "account": account or "",
    "password": password or "", })
  engine = WorkflowEngine(
    input_adapter=PyAutoGuiInputAdapter(),
    ocr_adapter=TesseractOCRAdapter(),
    match_adapter=PyAutoGuiMatchAdapter(),
  )
  result = engine.execute(workflow, context)
  print(f"Workflow success: {result.success}, message: {result.message}")
  if context.logs:
    print("Workflow logs:")
    for line in context.logs:
      print(f"  - {line}")

  if not result.success:
    raise RuntimeError(result.message)
