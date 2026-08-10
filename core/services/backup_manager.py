import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile

import win32com.client
from PyQt5.QtCore import QObject, pyqtSignal

from core.services.config_manager import ConfigManager
from core.services.path_manager import PathManager
from locales.localization import _

logger = logging.getLogger(__name__)


class BackupManager(QObject):
    """Handles application backup compression and decompression using 7-Zip."""

    progress_changed = pyqtSignal(int)      # Percentage progress (0-100)
    status_changed = pyqtSignal(str)        # Status message updates
    # Operation completion (Success, Message)
    finished = pyqtSignal(bool, str)

    # Conflict signals: Name, Zip Version, DB Version, Message
    ask_user_conflict = pyqtSignal(str, str, str, str)

    def __init__(self, db_manager, config_manager=None):
        super().__init__()
        self.db = db_manager
        self.config = config_manager if config_manager is not None else ConfigManager()

    def get_folder_size(self, path):
        """Calculates total directory size in bytes."""
        total_size = 0
        if not os.path.exists(path):
            return 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def export_to_zip(self, selected_apps, output_zip_path):
        """Exports selected applications to a compressed archive using 7za.exe."""

        logger.debug("STARTING EXPORT PROCESS WITH 7-ZIP")
        logger.debug(f"Output path: {output_zip_path}")
        logger.debug(f"Apps for export: {selected_apps}")

        if not selected_apps:
            self.finished.emit(
                False, _("bak_err_no_apps_export", "No applications selected for export."))
            return

        total_apps = len(selected_apps)

        # Locate 7za.exe in the bin directory
        seven_zip_path = PathManager.get_bin_path("7za.exe")

        if not os.path.exists(seven_zip_path):
            self.finished.emit(
                False, _("bak_err_7za_not_found", "7za.exe not found at path: {path}").format(path=seven_zip_path))
            return

        # Read and include Settings (excluding local install_path)
        app_config = {
            key: value
            for key, value in self.config.items()
            if key != "install_path"
        }

        manifest_data = {
            "wizard_version": "1.0",
            "config": app_config,
            "apps": []
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Created temporary working directory: {temp_dir}")

            for index, item in enumerate(selected_apps):
                app_name = item.get("name") if isinstance(item, dict) else item
                self.status_changed.emit(
                    _("bak_status_preparing", "Preparing: {app_name}...").format(app_name=app_name))

                app_info = self.db.get_app_by_name(app_name)
                if not app_info:
                    logger.warning(
                        f"Application '{app_name}' not found in database.")
                    continue

                full_local_path = app_info.get("local_path")
                full_exe_path = app_info.get("exe_path")

                if not full_local_path or not os.path.isdir(full_local_path):
                    logger.warning(
                        f"Directory '{full_local_path}' does not exist.")
                    continue

                # Calculate Portable relative paths
                folder_name = os.path.basename(
                    os.path.normpath(full_local_path))
                exe_filename = os.path.basename(
                    full_exe_path) if full_exe_path else ""
                relative_exe_path = f"{folder_name}/{exe_filename}" if exe_filename else ""

                app_manifest_entry = {
                    "name": app_info.get("name"),
                    "local_path": folder_name,
                    "exe_path": relative_exe_path,
                    "source": app_info.get("source", "manual"),
                    "update_url": app_info.get("update_url", ""),
                    "current_version": app_info.get("current_version", "1.0"),
                    "latest_version": app_info.get("latest_version", "1.0"),
                    "homepage": app_info.get("homepage", ""),
                    "size_bytes": self.get_folder_size(full_local_path)
                }
                manifest_data["apps"].append(app_manifest_entry)

                self.status_changed.emit(
                    _("bak_status_copying", "Copying files: {app_name}...").format(app_name=app_name))
                dest_temp_app_folder = os.path.join(temp_dir, folder_name)
                try:
                    shutil.copytree(full_local_path, dest_temp_app_folder)
                except Exception as e:
                    logger.warning(
                        f"Error during temporary copy of {app_name}: {e}")
                    continue

                progress = int((index + 1) / total_apps * 40)
                self.progress_changed.emit(progress)

            self.status_changed.emit(
                _("bak_status_manifest", "Creating manifest.json..."))
            manifest_path = os.path.join(temp_dir, "manifest.json")
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                self.finished.emit(
                    False, _("bak_err_manifest_fail", "Failed to create manifest.json: {error}").format(error=e))
                return

            self.status_changed.emit(
                _("bak_status_compressing", "Starting compression (Please wait)..."))
            self.progress_changed.emit(50)

            try:
                if output_zip_path.lower().endswith(".7z"):
                    self.status_changed.emit(
                        _("bak_status_compressing_7z", "Starting Ultra 7-Zip compression (Please wait)..."))
                    compression_type = "-t7z"
                    compression_level = "-mx=9"
                else:
                    self.status_changed.emit(
                        _("bak_status_compressing_zip", "Starting Fast ZIP compression..."))
                    compression_type = "-tzip"
                    compression_level = "-mx=5"

                command = [
                    seven_zip_path,
                    "a",
                    compression_type,
                    compression_level,
                    "-y",
                    output_zip_path,
                    os.path.join(temp_dir, "*")
                ]

                logger.debug(f"Executing command: {' '.join(command)}")

                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo,
                    text=True
                )

                self.progress_changed.emit(75)
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    logger.info("7-Zip compression completed successfully.")
                    self.progress_changed.emit(100)
                    self.finished.emit(
                        True, _("bak_msg_export_success", "Export completed successfully via 7-Zip!\nFile: {filename}").format(filename=os.path.basename(output_zip_path)))
                else:
                    logger.error(
                        f"7-Zip returned error code {process.returncode}: {stderr}")
                    self.finished.emit(
                        False, _("bak_err_7z_error", "7-Zip error: {error}").format(error=stderr if stderr else stdout))

            except Exception as e:
                logger.error(
                    f"Critical error during 7z subprocess execution: {e}", exc_info=True)
                self.finished.emit(False, _(
                    "bak_err_7z_call_fail", "7-Zip call failed: {error}").format(error=str(e)))

    def _import_app_settings(self, imported_config):
        """Merges imported settings into the local configuration, excluding local-specific paths."""
        try:
            if self.config is None:
                self.config = ConfigManager()

            for key, value in imported_config.items():
                if key != "install_path":
                    self.config[key] = value
            self.config.save()
            logger.debug("Application settings imported successfully.")
        except Exception as e:
            logger.error(f"Error during settings import: {e}", exc_info=True)

    def import_from_zip(self, source_path, dest_path, selected_apps, import_settings=False):
        """Restores selected applications from a backup archive."""

        logger.debug("STARTING IMPORT PROCESS")
        logger.debug(f"File: {source_path}")

        if not selected_apps:
            self.finished.emit(
                False, _("bak_err_no_apps_import", "No applications selected for import."))
            return

        self.status_changed.emit(
            _("bak_status_prep_extract", "Preparing extraction..."))
        self.progress_changed.emit(10)

        seven_zip_path = PathManager.get_bin_path("7za.exe")

        if not os.path.exists(seven_zip_path):
            self.finished.emit(
                False, _("bak_err_7za_not_found", "7za.exe not found at path: {path}").format(path=seven_zip_path))
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            self.status_changed.emit(
                _("bak_status_extracting", "Extracting file (Please wait)..."))

            command = [seven_zip_path, "x", source_path, f"-o{temp_dir}", "-y"]

            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startupinfo, text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.finished.emit(
                    False, _("bak_err_7z_error", "7-Zip error: {error}").format(error=stderr if stderr else stdout))
                return

            self.progress_changed.emit(40)
            self.status_changed.emit(
                _("bak_status_reading_manifest", "Reading settings (manifest.json)..."))

            manifest_path = os.path.join(temp_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                self.finished.emit(
                    False, _("bak_err_invalid_backup", "File does not contain manifest.json. Invalid backup."))
                return

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            if import_settings and "config" in manifest_data:
                self._import_app_settings(manifest_data["config"])

            apps_in_manifest = manifest_data.get("apps", [])
            total_apps = len(selected_apps)

            for index, app_name in enumerate(selected_apps):
                self.status_changed.emit(
                    _("bak_status_installing", "Installing: {app_name}...").format(app_name=app_name))

                app_info = next(
                    (app for app in apps_in_manifest if app["name"] == app_name), None)
                if not app_info:
                    logger.warning(
                        f"Application {app_name} not found in manifest.")
                    continue

                source_app_dir = os.path.join(temp_dir, app_info["local_path"])
                dest_app_dir = os.path.join(dest_path, app_info["local_path"])

                if os.path.exists(source_app_dir):
                    if os.path.exists(dest_app_dir):
                        shutil.rmtree(dest_app_dir)
                    shutil.copytree(source_app_dir, dest_app_dir)

                new_local_path = dest_app_dir.replace("\\", "/")
                new_exe_path = os.path.join(dest_path, app_info["exe_path"]).replace(
                    "\\", "/") if app_info.get("exe_path") else ""

                try:
                    self.db.add_or_update_app(
                        name=app_info["name"],
                        local_path=new_local_path,
                        exe_path=new_exe_path,
                        source=app_info.get("source", "manual"),
                        update_url=app_info.get("update_url", ""),
                        current_version=app_info.get("current_version", "1.0"),
                        latest_version=app_info.get("latest_version", "1.0"),
                        homepage=app_info.get("homepage", "")
                    )
                except Exception as db_err:
                    logger.error(
                        f"Error adding {app_name} to database: {db_err}", exc_info=True)

                # Register shortcuts
                try:
                    if new_exe_path and os.path.exists(new_exe_path):
                        apps_dir = os.path.abspath(
                            os.path.join(dest_path, "__Apps__"))
                        if not os.path.exists(apps_dir):
                            os.makedirs(apps_dir)

                        safe_app_name = "".join(
                            [c for c in app_info["name"] if c.isalnum() or c in (' ', '-', '_')]).strip()
                        shortcut_path = os.path.join(
                            apps_dir, f"{safe_app_name}.lnk")

                        shell = win32com.client.Dispatch("WScript.Shell")
                        shortcut = shell.CreateShortCut(shortcut_path)
                        shortcut.TargetPath = os.path.normpath(new_exe_path)
                        shortcut.WorkingDirectory = os.path.normpath(
                            new_local_path)
                        shortcut.save()
                        logger.debug(
                            f"Created shortcut (win32com): {app_info['name']} -> {shortcut_path}")
                except Exception as link_err:
                    logger.warning(
                        f"Error creating shortcut for {app_info['name']}: {link_err}")

                progress = 40 + int((index + 1) / total_apps * 50)
                self.progress_changed.emit(progress)

            self.progress_changed.emit(100)
            self.finished.emit(
                True, _("bak_msg_import_success", "Import completed successfully!"))
