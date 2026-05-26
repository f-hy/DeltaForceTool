"""Tests for workflow execution engine."""

from pathlib import Path

from deltaforcetool.automation.engine import WorkflowEngine
from deltaforcetool.automation.models import Rect, WorkflowDefinition, WorkflowStep
from deltaforcetool.automation.runtime import WorkflowRuntimeContext
class FakeInput:
  def __init__(self) -> None:
    self.events: list[str] = []

  def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
    self.events.append(f"click:{x}:{y}:{button}:{clicks}")

  def press(self, key: str) -> None:
    self.events.append(f"press:{key}")

  def type_text(self, value: str) -> None:
    self.events.append(f"type:{value}")
class FakeOCR:
  def __init__(self) -> None:
    self.calls = 0

  def read_text(self, region: tuple[int, int, int, int]) -> str:
    self.calls += 1
    if self.calls == 1:
      return "loading"
    return "ready 登录"
class FakeMatch:
  def locate(self, template_path: Path, region: tuple[int, int, int, int] | None = None) -> tuple[int, int] | None:
    return (777, 888)
def test_engine_runs_relative_click_and_wait_for_text() -> None:
  engine = WorkflowEngine(input_adapter=FakeInput(), ocr_adapter=FakeOCR(), match_adapter=FakeMatch())
  workflow = WorkflowDefinition(
    workflow_id="flow",
    name="Flow",
    anchor=Rect(100, 200, 800, 600),
    start_step="wait",
    steps=[
      WorkflowStep(
        id="wait",
        action="wait_for_text",
        params={
          "text": "登录",
          "timeout_ms": 1200,
          "interval_ms": 10,
          "region": {
            "left": 0,
            "top": 0,
            "width": 200,
            "height": 100,
            "relative": True}, },
        next_step="click1",
      ),
      WorkflowStep(
        id="click1",
        action="click",
        params={
          "x": 10,
          "y": 20,
          "relative": True,
          "button": "left",
          "clicks": 2},
      ), ],
  )

  context = WorkflowRuntimeContext()
  result = engine.execute(workflow, context)

  assert result.success is True
  assert result.executed_steps == ["wait", "click1"]
  fake_input = engine.input_adapter
  assert isinstance(fake_input, FakeInput)
  assert fake_input.events == ["click:110:220:left:2"]
def test_engine_branch_condition() -> None:
  input_adapter = FakeInput()
  engine = WorkflowEngine(input_adapter=input_adapter, ocr_adapter=FakeOCR(), match_adapter=FakeMatch())
  workflow = WorkflowDefinition(
    workflow_id="branch",
    name="Branch",
    anchor=Rect(0, 0, 100, 100),
    start_step="set",
    steps=[
      WorkflowStep(id="set", action="set_var", params={
        "name": "account",
        "value": "abc"}, next_step="branch"),
      WorkflowStep(
        id="branch",
        action="branch_if",
        params={"condition": "not_empty:account"},
        on_success="ok",
        on_failure="fail",
      ),
      WorkflowStep(id="ok", action="key_press", params={"key": "enter"}),
      WorkflowStep(id="fail", action="key_press", params={"key": "esc"}), ],
  )

  result = engine.execute(workflow)
  assert result.success is True
  assert input_adapter.events == ["press:enter"]
