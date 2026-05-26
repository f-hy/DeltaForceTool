# tests/tools/ocr/test_ocr_tool.py
"""Tests for OCRTool."""

import pytest

from deltaforcetool.tools.ocr import OCRTool
class TestOCRTool:
  """Test cases for OCRTool class."""
  def test_tool_name(self):
    """Test that tool has correct name."""
    assert OCRTool.name == "ocr"

  def test_init(self):
    """Test tool initialization."""
    tool = OCRTool()
    assert tool._running is False
    assert tool._detector is not None

  def test_stop_before_run(self):
    """Test stopping tool before running."""
    tool = OCRTool()
    tool.stop() # Should not raise

  @pytest.mark.skip(reason="UI testing requires display")
  def test_run_starts_tool(self):
    """Test that run sets _running to True."""
    tool = OCRTool()
    tool.run()
    assert tool._running is True
