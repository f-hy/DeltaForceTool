# tests/time/test_models.py
from deltaforcetool.utils.time import TimeConfig, TimeEvent
from datetime import datetime


def test_timeconfig_defaults():
    """Test TimeConfig default values."""
    config = TimeConfig()
    assert config.timezone == "Asia/Shanghai"
    assert config.update_interval_ms == 100


def test_timeconfig_custom():
    """Test TimeConfig custom values."""
    config = TimeConfig(
        timezone="UTC",
        update_interval_ms=500
    )
    assert config.timezone == "UTC"
    assert config.update_interval_ms == 500


def test_timeevent_creation():
    """Test TimeEvent creation."""
    now = datetime.now()
    event = TimeEvent(
        timestamp=now.timestamp(),
        current_time=now,
        formatted_time="12:34:56",
        timezone="Asia/Shanghai"
    )
    assert event.formatted_time == "12:34:56"
    assert event.timezone == "Asia/Shanghai"
