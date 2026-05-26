"""Automation workflow execution and persistence package."""

from .engine import WorkflowEngine
from .models import Rect, WorkflowDefinition, WorkflowResult, WorkflowStep
from .persistence import WorkflowStore
from .recorder import interactive_record_workflow
from .recorder_ui import launch_recorder_overlay
from .runtime import (
  PyAutoGuiInputAdapter,
  PyAutoGuiMatchAdapter,
  TesseractOCRAdapter,
  WorkflowRuntimeContext,
)
__all__ = [
  "Rect",
  "WorkflowDefinition",
  "WorkflowResult",
  "WorkflowStep",
  "WorkflowStore",
  "WorkflowEngine",
  "WorkflowRuntimeContext",
  "PyAutoGuiInputAdapter",
  "PyAutoGuiMatchAdapter",
  "TesseractOCRAdapter",
  "interactive_record_workflow",
  "launch_recorder_overlay", ]
