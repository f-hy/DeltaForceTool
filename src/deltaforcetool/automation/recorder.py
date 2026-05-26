"""Interactive recorder for creating workflow JSON files."""

from __future__ import annotations

from deltaforcetool.automation.models import Rect, WorkflowDefinition, WorkflowStep
from deltaforcetool.automation.persistence import WorkflowStore
def interactive_record_workflow(workflow_id: str, name: str | None = None) -> str:
  """Record workflow steps via terminal prompts and save JSON."""
  title = name or workflow_id
  print("Workflow recorder started. 输入空 action 结束。")
  anchor_left = int(input("anchor.left: ").strip() or "0")
  anchor_top = int(input("anchor.top: ").strip() or "0")
  anchor_width = int(input("anchor.width: ").strip() or "1920")
  anchor_height = int(input("anchor.height: ").strip() or "1080")

  steps: list[WorkflowStep] = []
  while True:
    action = input("step.action (click/key_press/type_text/wait_ms/wait_for_text/ocr_text/branch_if/image_match_click): ").strip()
    if not action:
      break

    step_id = input("step.id: ").strip()
    next_step = input("step.next_step (optional): ").strip() or None
    on_success = input("step.on_success (optional): ").strip() or None
    on_failure = input("step.on_failure (optional): ").strip() or None

    params_text = input("step.params JSON (default {}): ").strip() or "{}"
    try:
      import json

      params = json.loads(params_text)
      if not isinstance(params, dict):
        raise ValueError("params must be JSON object")
    except Exception as exc:
      raise ValueError(f"Invalid params JSON: {exc}") from exc

    steps.append(WorkflowStep(
      id=step_id,
      action=action,
      params=params,
      next_step=next_step,
      on_success=on_success,
      on_failure=on_failure,
    ))

  if not steps:
    raise ValueError("No steps recorded")

  workflow = WorkflowDefinition(
    workflow_id=workflow_id,
    name=title,
    anchor=Rect(anchor_left, anchor_top, anchor_width, anchor_height),
    steps=steps,
    start_step=steps[0].id,
  )

  store = WorkflowStore()
  target = store.save(workflow)
  return str(target)
