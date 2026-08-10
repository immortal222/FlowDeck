import logging
import os
from pathlib import Path

from core.utils import get_safe_folder_path

logger = logging.getLogger(__name__)


class FolderRenamer:
    """Handles safe folder naming and path normalization for portable applications."""

    def get_safe_folder_path(self, base_dir, desired_name, current_path=None):
        return get_safe_folder_path(base_dir, desired_name, current_path)

    def rename_folder(self, folder_path, desired_name, exe_path=None):
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return str(folder.resolve()).replace("\\", "/"), exe_path

        base_dir = folder.parent
        safe_path = self.get_safe_folder_path(
            str(base_dir), desired_name, str(folder))
        safe_path_obj = Path(safe_path)

        if safe_path_obj.resolve() == folder.resolve():
            return str(folder.resolve()).replace("\\", "/"), exe_path

        try:
            os.rename(folder, safe_path_obj)
            actual_exe_path = None
            if exe_path:
                try:
                    relative_exe = Path(exe_path).relative_to(folder)
                    actual_exe_path = str(
                        (safe_path_obj / relative_exe).resolve()).replace("\\", "/")
                except Exception:
                    actual_exe_path = str(
                        Path(exe_path).resolve()).replace("\\", "/")
            return str(safe_path_obj.resolve()).replace("\\", "/"), actual_exe_path or str(Path(exe_path).resolve()).replace("\\", "/") if exe_path else None
        except Exception as exc:
            logger.warning(
                f"Failed to rename folder '{folder}' to '{safe_path_obj}': {exc}")
            return str(folder.resolve()).replace("\\", "/"), exe_path
