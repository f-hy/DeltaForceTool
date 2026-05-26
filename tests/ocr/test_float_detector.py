#!/usr/bin/env python3
"""Test OCR float detection on selected_region.png"""

from pathlib import Path
from PIL import Image

import pytest

from deltaforcetool.tools.ocr.float_detector import FloatDetector
class TestFloatDetector:
  """Tests for FloatDetector."""
  @pytest.fixture
  def detector(self):
    """Create a FloatDetector instance."""
    return FloatDetector()

  @pytest.fixture
  def selected_region_image(self):
    """Load the test image."""
    image_path = Path(__file__).parent.parent.parent / "data" / "tmp" / "selected_region.png"
    assert image_path.exists(), f"Test image not found: {image_path}"
    return Image.open(image_path)

  def test_extract_floats_from_selected_region(self, detector: FloatDetector, selected_region_image: Image.Image) -> None:
    """Test OCR on selected_region.png."""
    # Test full image as region
    region = (0, 0, selected_region_image.size[0], selected_region_image.size[1])
    results = detector.extract_floats_from_region(selected_region_image, region)

    print(f"\nDetected {len(results)} float numbers:")
    for r in results:
      print(f"  - {r.value} at ({r.x}, {r.y})")

    # Assert we detected at least one float
    assert len(results) > 0, "No floats detected from selected_region.png"

    # Assert all values are valid floats
    for r in results:
      assert isinstance(r.value, float)
      assert r.width > 0
      assert r.height > 0
