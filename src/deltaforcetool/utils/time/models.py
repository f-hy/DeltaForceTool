# src/deltaforcetool/utils/time/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
@dataclass
class TimeConfig:
  """Time configuration settings."""

  timezone: str = "Asia/Shanghai"
  update_interval_ms: int = 100 # 100ms = 1/10s refresh rate
@dataclass
class TimeEvent:
  """Time event for observer notifications."""

  timestamp: float
  current_time: datetime
  formatted_time: str
  timezone: str
