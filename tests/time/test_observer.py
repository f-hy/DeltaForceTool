# tests/time/test_observer.py
from unittest.mock import Mock
from datetime import datetime
from deltaforcetool.utils.time import Subject, Observer, TimeEvent
class MyTestSubject(Subject):
  """Test concrete Subject implementation."""
  def __init__(self):
    self._observers = []

  def subscribe(self, observer: Observer) -> None:
    self._observers.append(observer)

  def unsubscribe(self, observer: Observer) -> None:
    self._observers.remove(observer)

  def notify(self, event: TimeEvent) -> None:
    for observer in self._observers:
      observer.update(event)
def test_observer_subscription():
  """Test observer subscription."""
  subject = MyTestSubject()
  observer = Mock()
  event = TimeEvent(timestamp=1234567890.0, current_time=datetime.now(), formatted_time="12:34:56", timezone="UTC")

  subject.subscribe(observer)
  subject.notify(event)
  observer.update.assert_called_once_with(event)
def test_observer_unsubscription():
  """Test observer unsubscription."""
  subject = MyTestSubject()
  observer = Mock()
  event = TimeEvent(timestamp=1234567890.0, current_time=datetime.now(), formatted_time="12:34:56", timezone="UTC")

  subject.subscribe(observer)
  subject.unsubscribe(observer)
  subject.notify(event)
  observer.update.assert_not_called()
