import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AppRepository:
    """Wraps database persistence operations for portable apps."""

    def __init__(self, db_manager):
        self.db = db_manager

    def create_backup(self):
        return self.db.create_backup()

    def get_all_apps(self):
        return self.db.get_all_apps()

    def get_app_by_name(self, name):
        return self.db.get_app_by_name(name)

    def delete_app(self, name):
        return self.db.delete_app(name)

    def increment_usage(self, name):
        self.db.increment_usage(name)

    def update_latest_version(self, name, latest_version, homepage=""):
        return self.db.update_latest_version(name, latest_version, homepage)

    def toggle_favorite(self, app_id, status):
        self.db.toggle_favorite(app_id, status)

    def update_app_details(self, app_id, name, version, exe_path):
        return self.db.update_app_details(app_id, name, version, exe_path)

    def get_registered_directories(self):
        directories = set()
        try:
            for app in self.db.get_all_apps():
                local_path = app.get("local_path")
                if local_path:
                    resolved = Path(local_path).resolve()
                    directories.add(str(resolved).replace("\\", "/").lower())
        except Exception as exc:
            logger.error(f"Failed to retrieve registered directories: {exc}")
        return directories

    def cleanup_orphaned_records(self, install_path):
        removed_count = 0
        current_base_path = None
        if install_path:
            try:
                current_base_path = Path(install_path).resolve()
            except Exception:
                current_base_path = None

        apps = self.db.get_all_apps()
        for app in apps:
            app_id = app.get("id")
            app_name = app.get("name")
            local_path = app.get("local_path")
            exe_path = app.get("exe_path")

            if not local_path:
                self.db.delete_app(app_name)
                removed_count += 1
                continue

            local_path_obj = Path(local_path)
            is_orphan = not local_path_obj.exists() or (
                exe_path and not Path(exe_path).exists())
            is_from_old_path = False

            if not is_orphan and current_base_path:
                try:
                    app_path = local_path_obj.resolve()
                    if not app_path.is_relative_to(current_base_path):
                        is_from_old_path = True
                except Exception:
                    is_from_old_path = False

            if is_orphan or is_from_old_path:
                self.db.delete_app(app_name)
                removed_count += 1

        logger.info(f"Total removed from database: {removed_count}")
        return removed_count

    def cleanup_orphaned_shortcuts(self, install_path):
        """Removes shortcut files in __Apps__ that are no longer registered in the database."""
        shortcut_count = 0
        if not install_path:
            return shortcut_count

        apps_dir = Path(install_path) / "__Apps__"
        if not apps_dir.exists() or not apps_dir.is_dir():
            return shortcut_count

        registered_names = set()
        registered_targets = set()
        for app in self.db.get_all_apps():
            name = app.get("name", "")
            if name:
                registered_names.add(name.lower())

            exe_path = app.get("exe_path")
            if exe_path:
                registered_targets.add(self._normalize_path(exe_path))

            local_path = app.get("local_path")
            if local_path:
                registered_targets.add(self._normalize_path(local_path))

        for pattern in ("*.lnk", "*.ink"):
            for shortcut_file in apps_dir.glob(pattern):
                if not shortcut_file.is_file():
                    continue

                file_name = shortcut_file.stem.lower()
                target_path = self._resolve_shortcut_target(shortcut_file)
                normalized_target = self._normalize_path(
                    target_path) if target_path else None

                if file_name in registered_names:
                    if normalized_target and normalized_target in registered_targets:
                        continue
                    if target_path is None:
                        # Preserve shortcut if we cannot resolve its target.
                        continue
                elif normalized_target and normalized_target in registered_targets:
                    continue

                try:
                    shortcut_file.unlink()
                    shortcut_count += 1
                    logger.info(f"Removed orphan shortcut: {shortcut_file}")
                except Exception as exc:
                    logger.warning(
                        f"Failed to remove shortcut {shortcut_file}: {exc}")

        return shortcut_count

    def _normalize_path(self, path):
        try:
            return str(Path(path).resolve()).replace("\\", "/").lower()
        except Exception:
            return str(path).replace("\\", "/").lower()

    def _resolve_shortcut_target(self, shortcut_file):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_file))
            target_path = shortcut.TargetPath
            return target_path if target_path else None
        except Exception as exc:
            logger.debug(
                f"Could not resolve shortcut target for {shortcut_file}: {exc}")
            return None

    def add_or_update_app(self, name, local_path, exe_path, source="manual", update_url="", current_version="1.0", latest_version=None, homepage=""):
        return self.db.add_or_update_app(
            name=name,
            local_path=local_path,
            exe_path=exe_path,
            source=source,
            update_url=update_url,
            current_version=current_version,
            latest_version=latest_version,
            homepage=homepage
        )

    def register_app(self, name, local_path, exe_path, source="manual", current_version="1.0", latest_version=None, homepage=""):
        return self.add_or_update_app(
            name=name,
            local_path=local_path,
            exe_path=exe_path,
            source=source,
            current_version=current_version,
            latest_version=latest_version,
            homepage=homepage
        )
