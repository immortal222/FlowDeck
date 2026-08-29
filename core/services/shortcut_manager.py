# Standard Library Imports
import logging
import re
from pathlib import Path

# Local Module Imports
from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class ShortcutManager:
    """Creates and verifies Windows shortcut files for portable applications."""

    def _sanitize_name(self, name):
        if not name:
            return ""
        safe_name = re.sub(r'[\\/*?:"<>|]', "", name).strip()
        return safe_name or "app"

    def get_apps_dir(self, portable_root):
        return Path(portable_root) / "__Apps__"

    def get_shortcut_path(self, name, portable_root):
        safe_name = self._sanitize_name(name)
        return self.get_apps_dir(portable_root) / f"{safe_name}.lnk"

    def shortcut_exists(self, name, portable_root):
        shortcut_path = self.get_shortcut_path(name, portable_root)
        return shortcut_path.exists()

    def create_shortcut(self, name, target_path, portable_root):
        if not portable_root or not target_path:
            return False

        # Ensure target_path is resolved to an absolute path in memory
        abs_target_path = PathManager.to_absolute_path(target_path)

        target = Path(abs_target_path)
        if not target.exists():
            logger.warning(
                f"Shortcut target does not exist, skipping creation: {target}")
            return False

        apps_dir = self.get_apps_dir(portable_root)
        apps_dir.mkdir(parents=True, exist_ok=True)

        shortcut_path = self.get_shortcut_path(name, portable_root)
        if shortcut_path.exists():
            return True

        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(target)
            shortcut.WorkingDirectory = str(target.parent)
            shortcut.save()
            logger.info(f"Created shortcut: {shortcut_path}")
            return True
        except Exception as exc:
            logger.warning(f"Failed to create shortcut {shortcut_path}: {exc}")
            return False

    def ensure_shortcut(self, name, target_path, portable_root):
        if self.shortcut_exists(name, portable_root):
            return True
        return self.create_shortcut(name, target_path, portable_root)
