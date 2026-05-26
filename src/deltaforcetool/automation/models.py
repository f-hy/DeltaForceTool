"""Workflow model definitions for automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
@dataclass(frozen=True)
class Rect:
  """A rectangular screen region."""

  left: int
  top: int
  width: int
  height: int
@dataclass(frozen=True)
class WorkflowStep:
  """A single workflow step."""

  id: str
  action: str
  params: dict[str, Any] = field(default_factory=dict)
  next_step: str | None = None
  on_success: str | None = None
  on_failure: str | None = None
@dataclass(frozen=True)
class WorkflowDefinition:
  """Workflow declaration that can be persisted and replayed."""

  workflow_id: str
  name: str
  anchor: Rect
  steps: list[WorkflowStep]
  start_step: str
  schema_version: int = 1
@dataclass
class WorkflowResult:
  """Execution result details."""

  success: bool
  executed_steps: list[str]
  failed_step: str | None = None
  message: str = ""
