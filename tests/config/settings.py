"""Configuration management for the test framework.

Provides environment-aware settings loaded from config.json.
Follows singleton pattern - import config from this module.
"""

import os
import json
from pathlib import Path

class Config:
    """Environment configuration for the test framework."""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "local").lower()
        self._data = self._load_config()

    def _load_config(self):
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                full = json.load(f)
                return  full.get("environments", {}).get(self.environment, {})
        return {}


    @property
    def base_url(self) -> str:
        return self._data.get("base_url", "")

    @property
    def admin_artist_email(self) -> str:
        return self._data.get("admin_artist_email", "")

    @property
    def admin_artist_password(self) -> str:
        return self._data.get("admin_artist_password", "")

    @property
    def admin_listener_email(self) -> str:
        return self._data.get("admin_listener_email", "")

    @property
    def admin_listener_password(self) -> str:
        return self._data.get("admin_listener_password", "")

    @property
    def admin_label_email(self) -> str:
        return self._data.get("admin_label_email", "")

    @property
    def admin_label_password(self) -> str:
        return self._data.get("admin_label_password", "")

config = Config()

