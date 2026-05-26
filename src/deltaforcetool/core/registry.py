# src/deltaforcetool/core/registry.py
from typing import Type, Dict, Any
class ToolRegistry:
  """Registry for managing tools using a factory-like pattern."""

  _tools: Dict[str, Type[Any]] = {}

  @classmethod
  def register(cls, name: str, tool_class: Type[Any]) -> None:
    """Register a tool class."""
    cls._tools[name] = tool_class

  @classmethod
  def get(cls, name: str) -> Any:
    """Get a tool instance by name."""
    if name not in cls._tools:
      raise KeyError(f"Tool '{name}' not registered")
    return cls._tools[name]()

  @classmethod
  def list_tools(cls) -> list[str]:
    """List all registered tool names."""
    return list(cls._tools.keys())

  @classmethod
  def clear(cls) -> None:
    """Clear all registered tools (for testing)."""
    cls._tools.clear()
