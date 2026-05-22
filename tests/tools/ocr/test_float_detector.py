# tests/tools/ocr/test_float_detector.py
"""Tests for FloatDetector."""

from pathlib import Path

import pytest
from PIL import Image

from deltaforcetool.tools.ocr import FloatDetector
from deltaforcetool.tools.ocr.float_detector import DetectionResult


class TestFloatDetector:
    """Test cases for FloatDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a FloatDetector instance."""
        return FloatDetector()

    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        img = Image.new('RGB', (100, 100), color='white')
        return img

    def test_init_default_paths(self, detector):
        """Test default initialization with proper paths."""
        assert detector.data_dir is not None
        assert detector.output_file is not None

    @pytest.mark.skip(reason="Tesseract OCR not installed")
    def test_extract_floats_from_empty_region(self, detector, sample_image):
        """Test extraction from region with no numbers."""
        results = detector.extract_floats_from_region(sample_image, (0, 0, 50, 50))
        assert isinstance(results, list)

    def test_save_results_appends(self, detector, sample_image, tmp_path):
        """Test that save_results appends to file."""
        # Override output file for testing
        test_output = tmp_path / "test_ocr.out"
        detector.output_file = test_output

        result1 = DetectionResult(value=1.23, x=0, y=0, width=10, height=10)
        result2 = DetectionResult(value=4.56, x=0, y=0, width=10, height=10)

        detector.save_results([result1])
        assert test_output.read_text() == "1.23\n"

        detector.save_results([result2])
        assert test_output.read_text() == "1.23\n4.56\n"
