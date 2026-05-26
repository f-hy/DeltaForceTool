"""Workflow persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path

from deltaforcetool.automation.models import Rect, WorkflowDefinition, WorkflowStep
from deltaforcetool.core.paths import get_project_paths
class WorkflowStore:
  """Load and save workflow definitions under data/inst."""
  def __init__(self, base_dir: Path | None = None) -> None:
    paths = get_project_paths()
    paths.ensure_data_dirs()
    self.base_dir = base_dir or paths.inst
    self.base_dir.mkdir(parents=True, exist_ok=True)

  def workflow_path(self, workflow_id: str) -> Path:
    """Resolve workflow file path by workflow id."""
    return self.base_dir / f"{workflow_id}.json"

  def save(self, workflow: WorkflowDefinition) -> Path:
    """Persist a workflow definition to disk."""
    payload = {
      "schema_version": workflow.schema_version,
      "workflow_id": workflow.workflow_id,
      "name": workflow.name,
      "anchor": {
        "left": workflow.anchor.left,
        "top": workflow.anchor.top,
        "width": workflow.anchor.width,
        "height": workflow.anchor.height, },
      "start_step": workflow.start_step,
      "steps": [{
        "id": step.id,
        "action": step.action,
        "params": step.params,
        "next_step": step.next_step,
        "on_success": step.on_success,
        "on_failure": step.on_failure, } for step in workflow.steps], }
    target = self.workflow_path(workflow.workflow_id)
    target.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return target

  def load(self, workflow_id: str) -> WorkflowDefinition:
    """Load a workflow by id."""
    return self.load_from_path(self.workflow_path(workflow_id))

  def load_from_path(self, path: Path) -> WorkflowDefinition:
    """Load a workflow from an explicit path."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    anchor = payload["anchor"]
    steps = [WorkflowStep(
      id=item["id"],
      action=item["action"],
      params=item.get("params", {}),
      next_step=item.get("next_step"),
      on_success=item.get("on_success"),
      on_failure=item.get("on_failure"),
    ) for item in payload["steps"]]

    return WorkflowDefinition(
      workflow_id=payload["workflow_id"],
      name=payload["name"],
      anchor=Rect(
        left=int(anchor["left"]),
        top=int(anchor["top"]),
        width=int(anchor["width"]),
        height=int(anchor["height"]),
      ),
      steps=steps,
      start_step=payload["start_step"],
      schema_version=int(payload.get("schema_version", 1)),
    )
