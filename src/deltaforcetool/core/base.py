# src/deltaforcetool/core/base.py
from abc import ABC, abstractmethod
class ITool(ABC):
  """Tool interface that all tools must implement."""
  @property
  @abstractmethod
  def name(self) -> str:
    """Return the tool name."""
    pass

  @abstractmethod
  def run(self) -> None:
    """Execute the tool."""
    pass

  @abstractmethod
  def stop(self) -> None:
    """Stop the tool execution."""
    pass
