"""Tests for CLI helper behavior."""

from deltaforcetool.app.cli import _looks_like_exe_path
def test_looks_like_exe_path() -> None:
  assert _looks_like_exe_path(r"C:\\Program Files\\WeGame\\wegame.exe") is True
  assert _looks_like_exe_path("D:/apps/wegame.exe") is True
  assert _looks_like_exe_path("clock") is False
