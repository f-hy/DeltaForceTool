# src/deltaforcetool/utils/time/observer.py
from abc import ABC, abstractmethod
from typing import Protocol, List
from datetime import datetime


class TimeEvent(Protocol):
    """Protocol for time event objects passed to observers."""

    @property
    def timestamp(self) -> float: ...
    @property
    def current_time(self) -> datetime: ...
    @property
    def formatted_time(self) -> str: ...
    @property
    def timezone(self) -> str: ...


class Observer(Protocol):
    """Observer protocol for time update notifications."""

    def update(self, event: TimeEvent) -> None:
        """Handle time event update."""
        pass


class Subject(ABC):
    """Subject interface for observable objects."""

    @abstractmethod
    def subscribe(self, observer: Observer) -> None:
        """Subscribe an observer."""
        pass

    @abstractmethod
    def unsubscribe(self, observer: Observer) -> None:
        """Unsubscribe an observer."""
        pass

    @abstractmethod
    def notify(self, event: TimeEvent) -> None:
        """Notify all subscribed observers."""
        pass
