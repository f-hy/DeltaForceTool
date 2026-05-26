"""Tests for application settings loading."""

import json

from deltaforcetool.core.settings import load_app_settings
def test_load_app_settings_uses_config_file(tmp_path) -> None:
  """Settings loader should parse the JSON config structure."""
  config_path = tmp_path / "keymap.json"
  config_path.write_text(
    json.dumps({
      "hotkeys": {
        "ocr_trigger": "alt+x",
        "exit": "ctrl+shift+q"},
      "ocr_settings": {
        "overlay_alpha": 0.5,
        "rect_color": "#112233",
        "rect_width": 5,
        "rect_dash": [1, 2], }, }),
    encoding="utf-8",
  )

  settings = load_app_settings(config_path)

  assert settings.hotkeys.ocr_trigger == "alt+x"
  assert settings.hotkeys.exit == "ctrl+shift+q"
  assert settings.ocr.overlay_alpha == 0.5
  assert settings.ocr.rect_color == "#112233"
  assert settings.ocr.rect_width == 5
  assert settings.ocr.rect_dash == (1, 2)
