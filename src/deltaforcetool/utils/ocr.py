# src/deltaforcetool/utils/ocr.py
"""OCR utility functions."""

from pathlib import Path
from typing import List, Optional
def load_ocr_values(output_file: Optional[Path] = None) -> List[float]:
  """Load float values from ocr.out file.

    Args:
        output_file: Path to ocr.out file. Defaults to data/ocr.out in project root.

    Returns:
        List of float values
    """
  if output_file is None:
    project_root = Path(__file__).resolve().parents[3]
    output_file = project_root / "data" / "ocr.out"

  if not output_file.exists():
    return []

  values: List[float] = []
  with open(output_file, 'r', encoding='utf-8') as f:
    for line in f:
      line = line.strip()
      if line:
        try:
          values.append(float(line))
        except ValueError:
          continue

  return values
def calculate_mean(n: int, output_file: Optional[Path] = None) -> float:
  """Calculate mean of last n values from ocr.out.

    Args:
        n: Number of last values to calculate mean from
        output_file: Path to ocr.out file. Defaults to data/ocr.out in project root.

    Returns:
        Mean value

    Raises:
        ValueError: If no values available or n <= 0
    """
  if n <= 0:
    raise ValueError("n must be positive")

  values = load_ocr_values(output_file)

  if not values:
    raise ValueError("No values found in ocr.out")

  if n > len(values):
    n = len(values)

  last_n_values = values[-n:]
  return sum(last_n_values) / n
def print_mean(n: int, output_file: Optional[Path] = None) -> None:
  """Calculate and print mean of last n values.

    Args:
        n: Number of last values to calculate mean from
        output_file: Path to ocr.out file. Defaults to data/ocr.out in project root.
    """
  # Use project root default if no output_file specified
  if output_file is None:
    project_root = Path(__file__).resolve().parents[3]
    output_file = project_root / "data" / "ocr.out"

  try:
    values = load_ocr_values(output_file)
    if not values:
      print(f"Error: No values found in {output_file}")
      return

    if n > len(values):
      n = len(values)

    last_n_values = values[-n:]
    mean_val = sum(last_n_values) / n

    print(f"\n{'='*40}")
    print(f"Mean of last {n} values:")
    print(f"  Values: {last_n_values}")
    print(f"  Mean: {mean_val}")
    print(f"{'='*40}\n")
  except Exception as e:
    print(f"Error: {e}")
