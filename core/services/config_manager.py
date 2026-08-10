import json
import logging
import os

from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class ConfigManager:
    DEFAULT_CONFIG = {
        "install_path": os.path.expanduser("~/FlowDeck/Apps").replace("\\", "/"),
        "start_on_boot": False,
        "minimize_to_tray": True,
        "language": "English",
        "theme": "Modern Dark",
        "update_freq": "On Startup",
        "silent_updater": True,
        "update_to_start": True
    }

    def __init__(self):
        self.config_file = PathManager.get_config_path()
        self.data = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        self.data = self.DEFAULT_CONFIG.copy()

        if not os.path.exists(self.config_file):
            self.save()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                stored_config = json.load(f)

            if isinstance(stored_config, dict):
                self.data = {**self.DEFAULT_CONFIG, **stored_config}
            else:
                logger.warning(
                    "Config file is not a JSON object. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")

        self._ensure_install_path()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving config file: {e}")

    def reset_defaults(self):
        self.data = self.DEFAULT_CONFIG.copy()
        self.save()
        self._ensure_install_path()

    def _ensure_install_path(self):
        install_path = self.data.get("install_path")
        if install_path:
            try:
                os.makedirs(install_path, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create install path: {e}")

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default if default is not None else self.DEFAULT_CONFIG.get(key)

    def set(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def as_dict(self):
        return self.data.copy()
