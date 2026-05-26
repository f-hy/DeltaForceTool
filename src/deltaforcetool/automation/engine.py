"""Workflow execution engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from deltaforcetool.automation.models import WorkflowDefinition, WorkflowResult, WorkflowStep
from deltaforcetool.automation.runtime import (
  InputAdapter,
  MatchAdapter,
  OCRAdapter,
  WorkflowRuntimeContext,
  now_ms,
  sleep_ms,
)
@dataclass
class WorkflowEngine:
  """Execute workflow definitions against runtime adapters."""

  input_adapter: InputAdapter
  ocr_adapter: OCRAdapter
  match_adapter: MatchAdapter

  def execute(self, workflow: WorkflowDefinition, context: WorkflowRuntimeContext | None = None) -> WorkflowResult:
    """Run a workflow and return execution details."""
    runtime = context or WorkflowRuntimeContext()
    step_map = {step.id: step for step in workflow.steps}
    current = workflow.start_step
    executed: list[str] = []

    while current is not None:
      step = step_map.get(current)
      if step is None:
        return WorkflowResult(
          success=False,
          executed_steps=executed,
          failed_step=current,
          message=f"Step '{current}' not found",
        )

      executed.append(step.id)
      runtime.log(f"Running step {step.id} ({step.action})")
      success, message, next_step = self._run_step(step, workflow, runtime)
      runtime.log(message)

      if not success:
        if step.on_failure is not None:
          current = step.on_failure
          continue
        return WorkflowResult(
          success=False,
          executed_steps=executed,
          failed_step=step.id,
          message=message,
        )

      current = next_step

    return WorkflowResult(success=True, executed_steps=executed, message="Workflow completed")

  def _run_step(
    self,
    step: WorkflowStep,
    workflow: WorkflowDefinition,
    context: WorkflowRuntimeContext,
  ) -> tuple[bool, str, str | None]:
    action = step.action
    params = dict(step.params)

    if action == "wait_ms":
      delay = int(params.get("ms", 0))
      sleep_ms(delay)
      return True, f"Waited {delay}ms", step.next_step

    if action == "click":
      x, y = self._resolve_point(params, workflow)
      button = str(params.get("button", "left"))
      clicks = int(params.get("clicks", 1))
      self.input_adapter.click(x=x, y=y, button=button, clicks=clicks)
      return True, f"Clicked ({x}, {y}) with {button}", step.next_step

    if action == "key_press":
      key = str(params["key"])
      self.input_adapter.press(key)
      return True, f"Pressed key {key}", step.next_step

    if action == "type_text":
      value = self._resolve_text(params.get("value", ""), context)
      self.input_adapter.type_text(value)
      return True, "Typed text", step.next_step

    if action == "set_var":
      key = str(params["name"])
      value = self._resolve_text(params.get("value", ""), context)
      context.variables[key] = value
      return True, f"Set variable {key}", step.next_step

    if action == "ocr_text":
      region = self._resolve_region(params, workflow)
      text = self.ocr_adapter.read_text(region)
      if "var" in params:
        context.variables[str(params["var"])] = text
      return True, f"OCR text: {text}", step.next_step

    if action == "wait_for_text":
      target = str(params["text"])
      region = self._resolve_region(params, workflow)
      timeout_ms = int(params.get("timeout_ms", 10000))
      interval_ms = int(params.get("interval_ms", 400))
      matched = self._wait_for_text(target, region, timeout_ms, interval_ms, context)
      if not matched:
        return False, f"Timeout waiting for text: {target}", step.next_step
      post_delay = int(params.get("post_delay_ms", 0))
      sleep_ms(post_delay)
      return True, f"Detected text: {target}", step.next_step

    if action == "image_match_click":
      template = Path(str(params["template"]))
      if not template.is_absolute():
        template = Path(params.get("template_base", "")) / template
      region = self._resolve_region(params, workflow) if params.get("region") else None
      point = self.match_adapter.locate(template, region)
      if point is None:
        return False, f"Template not found: {template}", step.next_step
      self.input_adapter.click(x=point[0], y=point[1], button=str(params.get("button", "left")), clicks=1)
      return True, f"Clicked template {template}", step.next_step

    if action == "branch_if":
      condition = str(params.get("condition", ""))
      if self._evaluate_condition(condition, context):
        return True, "Branch true", step.on_success or step.next_step
      return True, "Branch false", step.on_failure or step.next_step

    return False, f"Unsupported action: {action}", step.next_step

  def _resolve_point(self, params: dict[str, object], workflow: WorkflowDefinition) -> tuple[int, int]:
    x = int(params.get("x", 0))
    y = int(params.get("y", 0))
    relative = bool(params.get("relative", True))
    if not relative:
      return x, y
    return workflow.anchor.left + x, workflow.anchor.top + y

  def _resolve_region(self, params: dict[str, object], workflow: WorkflowDefinition) -> tuple[int, int, int, int]:
    region = params.get("region")
    if not isinstance(region, dict):
      raise ValueError("region must be provided as object with left/top/width/height")

    left = int(region.get("left", 0))
    top = int(region.get("top", 0))
    width = int(region.get("width", 0))
    height = int(region.get("height", 0))
    relative = bool(region.get("relative", True))

    if relative:
      left += workflow.anchor.left
      top += workflow.anchor.top

    return left, top, width, height

  def _resolve_text(self, value: str, context: WorkflowRuntimeContext) -> str:
    text = str(value)
    for key, data in context.variables.items():
      text = text.replace(f"{{{{{key}}}}}", str(data))
    return text

  def _wait_for_text(
    self,
    target: str,
    region: tuple[int, int, int, int],
    timeout_ms: int,
    interval_ms: int,
    context: WorkflowRuntimeContext,
  ) -> bool:
    deadline = now_ms() + timeout_ms
    target_lower = target.lower()
    while now_ms() <= deadline:
      content = self.ocr_adapter.read_text(region)
      context.log(f"wait_for_text OCR='{content}'")
      if target_lower in content.lower():
        return True
      sleep_ms(interval_ms)
    return False

  def _evaluate_condition(self, condition: str, context: WorkflowRuntimeContext) -> bool:
    # Simple condition forms:
    # - not_empty:var_name
    # - equals:var_name:value
    # - contains:var_name:value
    if condition.startswith("not_empty:"):
      key = condition.split(":", 1)[1]
      return bool(str(context.variables.get(key, "")).strip())

    if condition.startswith("equals:"):
      _, key, expected = condition.split(":", 2)
      return str(context.variables.get(key, "")) == expected

    if condition.startswith("contains:"):
      _, key, expected = condition.split(":", 2)
      return expected in str(context.variables.get(key, ""))

    return False
