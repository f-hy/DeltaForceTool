"""Tests for project path helpers."""

from deltaforcetool.core.paths import get_project_paths
def test_project_paths_point_to_repo_root() -> None:
  """Project paths should resolve to the repository root layout."""
  paths = get_project_paths()

  assert (paths.root / "README.md").exists()
  assert paths.conf == paths.root / "conf"
  assert paths.data == paths.root / "data"
  assert paths.tmp == paths.data / "tmp"
  assert paths.models == paths.data / "models"
  assert paths.ocr_output == paths.data / "ocr.out"
