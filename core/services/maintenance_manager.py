import logging
import os
from pathlib import Path

from core.api.scoop_api import ScoopAPI
from core.services.app_repository import AppRepository
from core.services.folder_renamer import FolderRenamer
from core.services.portable_scanner import PortableScanner
from core.services.shortcut_manager import ShortcutManager

logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Maintains portable application records by scanning folders and syncing the database.

    Accepts optional helper instances to allow dependency injection from callers
    (useful for testing or when UI wants to reuse helpers directly).
    """

    def __init__(self, db_manager, config_dict, scanner=None, renamer=None, repository=None, scoop=None):
        self.db = db_manager
        self.config = config_dict
        # allow injection of helpers or create defaults
        self.scanner = scanner if scanner is not None else PortableScanner()
        self.renamer = renamer if renamer is not None else FolderRenamer()
        self.repository = repository if repository is not None else AppRepository(
            db_manager)
        self.scoop = scoop if scoop is not None else ScoopAPI()
        self.shortcut_manager = ShortcutManager()

    def execute_scan_and_repair(self, dialog_callback=None):
        """Scans the install directory, repairs orphaned records and registers discovered apps."""
        self.repository.create_backup()

        install_path = self.config.get("install_path", "")
        removed_count = self.repository.cleanup_orphaned_records(install_path)
        shortcut_removed = self.repository.cleanup_orphaned_shortcuts(
            install_path)
        added_count = 0

        if not install_path or not os.path.isdir(install_path):
            return True, removed_count + shortcut_removed, added_count, None

        registered_dirs = self.repository.get_registered_directories()

        for entry in os.scandir(install_path):
            if not entry.is_dir():
                continue

            entry_path = Path(entry.path).resolve()
            entry_path_str = str(entry_path).replace("\\", "/")

            if entry_path_str.lower() in registered_dirs:
                continue

            metadata = self.scanner.scan_folder_metadata(entry_path)
            if not metadata:
                continue

            final_name = metadata["name"]
            final_version = metadata["version"]
            actual_dir_path = entry_path_str
            actual_exe_path = metadata["exe_path"]
            is_paf = metadata.get("is_paf", False)

            if dialog_callback:
                approved, user_name, user_version = dialog_callback(
                    entry_path.name, final_name, final_version)
                if not approved:
                    continue
                final_name = user_name
                final_version = user_version

            scoop_data = self.scoop.search_app(final_name)
            is_scoop = isinstance(scoop_data, dict)
            latest_version = scoop_data.get("version") if is_scoop else None
            source = "scoop" if is_scoop else metadata.get(
                "source_hint", "manual")
            homepage = scoop_data.get("homepage") if is_scoop else ""

            if not is_paf:
                # Decide whether to physically rename the folder.
                base_directory = str(entry_path.parent).replace("\\", "/")
                # Ask renamer for a safe path without performing changes yet
                new_dir_path = self.renamer.get_safe_folder_path(
                    base_directory, final_name, actual_dir_path)

                # If the safe path differs from current and the target already exists
                # on disk but is NOT registered in the DB, skip renaming to avoid
                # creating "name 2" duplicates when the DB isn't in sync.
                if new_dir_path.lower() != actual_dir_path.lower():
                    if os.path.exists(new_dir_path) and new_dir_path.lower() not in registered_dirs:
                        logger.info(
                            f"Target folder '{new_dir_path}' exists on disk but is not registered; skipping physical rename.")
                        # keep actual_dir_path as-is
                    else:
                        renamed_dir, renamed_exe = self.renamer.rename_folder(
                            actual_dir_path, final_name, actual_exe_path)
                        actual_dir_path = renamed_dir
                        if renamed_exe:
                            actual_exe_path = renamed_exe

            success = self.repository.register_app(
                name=final_name,
                local_path=actual_dir_path,
                exe_path=actual_exe_path,
                source=source,
                current_version=final_version,
                latest_version=latest_version,
                homepage=homepage,
            )

            if success:
                added_count += 1
                registered_dirs.add(actual_dir_path.lower())
                if actual_exe_path:
                    self.shortcut_manager.ensure_shortcut(
                        final_name, actual_exe_path, install_path)
            else:
                logger.warning(
                    f"Failed to register app '{final_name}' from {actual_dir_path}")

        self._ensure_shortcuts_for_registered_apps(install_path)
        return True, removed_count + shortcut_removed, added_count, None

    def _ensure_shortcuts_for_registered_apps(self, install_path):
        apps = self.db.get_all_apps()
        for app in apps:
            app_name = app.get("name")
            exe_path = app.get("exe_path")
            if not app_name or not exe_path:
                continue
            if not os.path.exists(exe_path):
                continue
            self.shortcut_manager.ensure_shortcut(
                app_name, exe_path, install_path)
