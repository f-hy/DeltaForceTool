# src/deltaforcetool/utils/time/singleton.py
from abc import ABC, abstractmethod
from typing import TypeVar, Self, Any
T = TypeVar("T", bound="Singleton")
class Singleton(ABC):
  """Singleton pattern base class."""

  _instance: "Singleton | None" = None
  _initialized: bool = False

  def __new__(cls: type[T], *args: Any, **kwargs: Any) -> T:
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance # type: ignore

  def __init__(self, *args: Any, **kwargs: Any) -> None:
    if not type(self)._initialized:
      super().__init__()
      type(self)._initialized = True

  @classmethod
  @abstractmethod
  def instance(cls: type[T], *args: Any, **kwargs: Any) -> T:
    """Get the singleton instance."""
    pass
