"""Project path helpers."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
@dataclass(frozen=True)
class ProjectPaths:
  """Resolved project paths used across the application."""

  root: Path
  src: Path
  conf: Path
  data: Path
  tmp: Path
  models: Path
  ocr_output: Path

  def ensure_data_dirs(self) -> None:
    """Create the writable directories used by the app."""
    self.data.mkdir(parents=True, exist_ok=True)
    self.tmp.mkdir(parents=True, exist_ok=True)
    self.models.mkdir(parents=True, exist_ok=True)
@lru_cache(maxsize=1)
def get_project_paths() -> ProjectPaths:
  """Return the cached project paths."""
  root = Path(__file__).resolve().parents[3]
  src = root / "src"
  conf = root / "conf"
  data = root / "data"

  return ProjectPaths(
    root=root,
    src=src,
    conf=conf,
    data=data,
    tmp=data / "tmp",
    models=data / "models",
    ocr_output=data / "ocr.out",
  )
