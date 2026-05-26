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
        # Get project root - it's the parent of src/deltaforcetool
        project_root = Path(__file__).resolve().parents[4]
        self.model_dir = model_dir or project_root / "data" / "models"
        self.data_dir = project_root / "data"
        self.output_file = self.data_dir / "ocr.out"

        # Configure Tesseract path for Windows
        import platform
        if platform.system() == "Windows":
            # Common Tesseract installation paths on Windows
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\frien\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
            ]
            for path in tesseract_paths:
                if Path(path).exists():
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"Tesseract path set to: {path}")
                    break
            else:
                print("Warning: Tesseract not found in common paths. Trying system PATH...")

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

        # Preprocessing: Convert to grayscale
        if cropped.mode != 'L':
            cropped_gray = cropped.convert('L')
        else:
            cropped_gray = cropped

        # Debug: Save original cropped image for inspection
        debug_path = self.data_dir / "tmp" / "cropped_region.png"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        cropped_gray.save(str(debug_path))
        print(f"Cropped region saved to {debug_path}")
        print(f"Cropped image size: {cropped_gray.size}, mode: {cropped_gray.mode}")

        # For white-on-dark images, we need to invert
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.-'

        # Try original image first
        text = pytesseract.image_to_string(cropped_gray, config=custom_config, lang='eng')
        print(f"Tesseract output (original): '{text}'")

        # Try with Otsu's thresholding after inversion
        if not text.strip():
            # Invert: dark text on light background
            inverted = cropped_gray.point(lambda p: 255 - p)
            inverted_path = self.data_dir / "tmp" / "inverted_region.png"
            inverted.save(str(inverted_path))
            print(f"Inverted image saved to {inverted_path}")

            # Use histogram analysis to find optimal threshold
            pixels = list(inverted.getdata())
            if not pixels:
                print("No pixels in image")
                self._cleanup_selection()
                self.stop()
                return

            # Calculate statistics
            min_val = min(pixels)
            max_val = max(pixels)
            mean_val = sum(pixels) / len(pixels)

            # Separate into text and background groups
            text_pixels = [p for p in pixels if p < 200]  # Assume text is darker
            bg_pixels = [p for p in pixels if p > 55]     # Assume background is lighter

            if text_pixels and bg_pixels:
                text_mean = sum(text_pixels) / len(text_pixels)
                bg_mean = sum(bg_pixels) / len(bg_pixels)
                # Use midpoint between text and background means as threshold
                optimal_threshold = (text_mean + bg_mean) / 2
            else:
                # Fallback: use Otsu's method - midpoint between min and max
                optimal_threshold = (min_val + max_val) / 2

            print(f"Pixel stats: min={min_val}, max={max_val}, mean={mean_val:.1f}, threshold={optimal_threshold:.1f}")

            # Create binary image with optimal threshold
            binary = inverted.point(lambda p: 255 if p > optimal_threshold else 0, '1')
            binary_path = self.data_dir / "tmp" / "binary_inverted_region.png"
            binary.save(str(binary_path))
            print(f"Binary inverted image saved to {binary_path}")

            text2 = pytesseract.image_to_string(binary, config=custom_config, lang='eng')
            print(f"Tesseract output (adaptive binary): '{text2}'")

            if text2.strip():
                text = text2

        # Fallback: simple inversion without binary
        if not text.strip():
            text = pytesseract.image_to_string(inverted if 'inverted' in dir() else cropped_gray, config=custom_config, lang='eng')
            print(f"Tesseract output (inverted fallback): '{text}'")

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

        print(f"Found {len(results)} float numbers: {[r.value for r in results]}")
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
