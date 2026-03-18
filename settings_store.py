from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR_NAME = ".video_to_frames_exporter"
SETTINGS_FILE_NAME = "settings.json"


def get_settings_path() -> Path:
    home = Path.home()
    app_dir = home / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / SETTINGS_FILE_NAME


def load_settings() -> dict[str, Any]:
    path = get_settings_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_settings(settings: dict[str, Any]) -> None:
    path = get_settings_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
