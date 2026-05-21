# tests/time/test_singleton.py
import pytest
from deltaforcetool.utils.time import Singleton


class MyTestSingleton(Singleton):
    """Test concrete singleton implementation."""

    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value

    @classmethod
    def instance(cls, value: int = 0) -> "TestSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(value)
        return cls._instance  # type: ignore


def test_singleton_returns_same_instance():
    """Test that singleton returns the same instance."""
    MyTestSingleton._instance = None  # Reset for clean test
    MyTestSingleton._initialized = False
    instance1 = MyTestSingleton.instance(10)
    instance2 = MyTestSingleton.instance(20)
    assert instance1 is instance2


def test_singleton_initialization():
    """Test singleton initialization."""
    MyTestSingleton._instance = None  # Reset for clean test
    MyTestSingleton._initialized = False
    instance = MyTestSingleton.instance(42)
    assert instance.value == 42
