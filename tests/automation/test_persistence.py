"""Tests for workflow persistence."""

from deltaforcetool.automation.models import Rect, WorkflowDefinition, WorkflowStep
from deltaforcetool.automation.persistence import WorkflowStore
def test_workflow_store_round_trip(tmp_path) -> None:
  store = WorkflowStore(tmp_path)
  workflow = WorkflowDefinition(
    workflow_id="demo",
    name="Demo workflow",
    anchor=Rect(0, 0, 1920, 1080),
    start_step="step1",
    steps=[
      WorkflowStep(id="step1", action="wait_ms", params={"ms": 10}, next_step="step2"),
      WorkflowStep(id="step2", action="key_press", params={"key": "enter"}), ],
  )

  target = store.save(workflow)
  loaded = store.load_from_path(target)

  assert loaded.workflow_id == "demo"
  assert loaded.name == "Demo workflow"
  assert loaded.start_step == "step1"
  assert len(loaded.steps) == 2
  assert loaded.steps[0].action == "wait_ms"
  assert loaded.steps[1].params["key"] == "enter"
