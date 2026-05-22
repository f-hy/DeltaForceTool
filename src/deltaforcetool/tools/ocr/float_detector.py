# src/deltaforcetool/tools/ocr/float_detector.py
"""Float number detection using OCR."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pytesseract
from PIL import Image


@dataclass
class DetectionResult:
    """Represents a detected float number."""

    value: float
    x: int
    y: int
    width: int
    height: int


class FloatDetector:
    """Detects float numbers in image regions using OCR."""

    # Regex pattern to match float numbers (including negative, with/without decimal)
    FLOAT_PATTERN = re.compile(r'-?\d+\.?\d*|\d*\.?\d+')

    def __init__(self, model_dir: Optional[Path] = None):
        """Initialize the float detector.

        Args:
            model_dir: Optional path to model directory for custom models
        """
        self.model_dir = model_dir or Path(__file__).parent.parent.parent / "data" / "models"
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.output_file = self.data_dir / "ocr.out"

    def extract_floats_from_region(
        self,
        image: Image.Image,
        region: Tuple[int, int, int, int]
    ) -> List[DetectionResult]:
        """Extract float numbers from a specific region of the image.

        Args:
            image: PIL Image object
            region: (x, y, width, height) tuple defining the detection region

        Returns:
            List of DetectionResult objects with value and position
        """
        x, y, w, h = region

        # Crop the region
        cropped = image.crop((x, y, x + w, y + h))

        # Use pytesseract to extract text with custom config for numbers
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.-'
        text = pytesseract.image_to_string(cropped, config=custom_config, lang='chi_sim+eng')

        # Find all float numbers in the text
        results = []
        for match in self.FLOAT_PATTERN.finditer(text):
            try:
                value = float(match.group())
                # Estimate position based on match position in cropped image
                results.append(DetectionResult(
                    value=value,
                    x=x + match.start(),
                    y=y + match.end(),  # Simplified positioning
                    width=match.end() - match.start(),
                    height=h
                ))
            except ValueError:
                continue

        return results

    def save_results(self, results: List[DetectionResult]) -> None:
        """Save detection results to output file (append mode).

        Args:
            results: List of DetectionResult objects to save
        """
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'a', encoding='utf-8') as f:
            for result in results:
                f.write(f"{result.value}\n")

    def detect_and_save(
        self,
        image: Image.Image,
        region: Tuple[int, int, int, int]
    ) -> List[DetectionResult]:
        """Detect floats in region and save results.

        Args:
            image: PIL Image object
            region: (x, y, width, height) tuple

        Returns:
            List of detected DetectionResult objects
        """
        results = self.extract_floats_from_region(image, region)
        if results:
            self.save_results(results)
        return results
