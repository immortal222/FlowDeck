# Standard Library Imports
import logging
import os
import shutil
import stat
import subprocess
import sys
import winreg

# Third-Party Imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QVBoxLayout)

# Local Module Imports
from core.services.app_repository import AppRepository
from core.services.folder_renamer import FolderRenamer
from core.services.maintenance_manager import MaintenanceManager
from core.services.portable_scanner import PortableScanner
from core.services.path_manager import PathManager
from core.services.system_stats_service import SystemStatsService
from core.services.constants import VERSION
from locales.localization import _
from locales.ui_localizer import localize_settings_page
from ui.dialogs.dialog_utils import ask_confirmation
from ui.pages.backup_wizard_controller import BackupWizardController
from ui.styles.styles import DIALOG_LIGHT_STYLE, DIALOG_STYLE


logger = logging.getLogger(__name__)


class ScanConfirmDialog(QDialog):
    """Dialog for confirming registration of newly discovered portable applications."""

    def __init__(self, folder_name, detected_name, detected_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            _("set_scan_confirm_title", "New Application Detected"))
        self.setMinimumWidth(400)

        theme = parent.settings_controller.config.get("theme", "Modern Dark") if hasattr(
            parent, 'settings_controller') else "Modern Dark"
        style = DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE
        self.setStyleSheet(style)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        lbl_info = QLabel(
            _("set_scan_detected_msg", "<b>🧹 New portable application found!</b>"))
        lbl_info.setStyleSheet("font-size: 14px; color: #2371C4;")
        layout.addWidget(lbl_info)

        layout.addWidget(QLabel(
            f"{_('set_scan_folder_label', 'Folder name on disk:')} <i>{folder_name}</i>"))

        layout.addWidget(
            QLabel(_("set_scan_name_field", "Application Name:")))
        self.txt_name = QLineEdit(detected_name)
        layout.addWidget(self.txt_name)

        layout.addWidget(
            QLabel(_("set_scan_version_field", "Version:")))
        self.txt_version = QLineEdit(detected_version)
        layout.addWidget(self.txt_version)

        btn_layout = QHBoxLayout()
        self.btn_confirm = QPushButton(
            _("set_scan_btn_register", "Register"))
        self.btn_confirm.setObjectName("primaryButton")
        self.btn_confirm.clicked.connect(self.accept)

        self.btn_cancel = QPushButton(_("set_scan_btn_skip", "Skip"))
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        layout.addLayout(btn_layout)

    def get_values(self):
        """Returns the updated user-provided metadata."""
        return self.txt_name.text().strip(), self.txt_version.text().strip()


class SettingsController:
    """Controller for managing application settings, themes, and maintenance tasks."""

    def __init__(self, main_window, config_manager):
        self.main_window = main_window
        self.ui = main_window.ui
        self.db = main_window.db
        self.config = config_manager

        # Initialize the SystemStatsService for gathering system statistics
        self.stats_service = SystemStatsService(self.db, self.config)

        localize_settings_page(self.main_window)

        self.setup_ui()
        self.populate_ui()

    def update_system_stats(self):
        """Updates all system analytics labels in the settings page UI."""
        stats = self.stats_service.get_all_stats()

        # Βασικές πληροφορίες
        if hasattr(self.ui, 'system_lbl_inst_app'):
            self.ui.system_lbl_inst_app.setText(
                str(stats.get('installed_apps', 0)))

        if hasattr(self.ui, 'system_lbl_update'):
            self.ui.system_lbl_update.setText(
                str(stats.get('need_updates', 0)))

        if hasattr(self.ui, 'system_lbl_favorites'):
            self.ui.system_lbl_favorites.setText(
                str(stats.get('favorites', 0)))

        if hasattr(self.ui, 'system_lbl_size'):
            self.ui.system_lbl_size.setText(
                str(stats.get('apps_folder_size', '0 MB')))

        if hasattr(self.ui, 'system_ldl_version'):
            self.ui.system_ldl_version.setText(VERSION)

        if hasattr(self.ui, 'system_lbl_dbcheck'):
            db_status = stats.get('db_status', 'OK')
            self.ui.system_lbl_dbcheck.setText(db_status)
            if db_status == "OK":
                self.ui.system_lbl_dbcheck.setStyleSheet(
                    "color: #41CD52; font-weight: bold;")
            else:
                self.ui.system_lbl_dbcheck.setStyleSheet(
                    "color: #E74C3C; font-weight: bold;")

        if hasattr(self.ui, 'system_lbl_scoopver'):
            self.ui.system_lbl_scoopver.setText(
                str(stats.get('scoop_version', 'N/A')))

        # Most Launched Apps (1-5)
        most_launched = stats.get('most_launched', ['-'] * 5)
        for i in range(1, 6):
            lbl_name = f'system_lbl_most{i}'
            if hasattr(self.ui, lbl_name):
                getattr(self.ui, lbl_name).setText(most_launched[i - 1])

        # Largest Folder Apps (1-5)
        # Σημείωση: Το 1ο σε μέγεθος είναι το system_lbl_size, γι' αυτό τα υπόλοιπα 4 αντιστοιχούν στο 2-5
        largest_apps = stats.get('largest_apps', ['-'] * 5)
        for i in range(1, 6):
            lbl_name = f'system_lbl_space{i}'
            if hasattr(self.ui, lbl_name):
                getattr(self.ui, lbl_name).setText(largest_apps[i - 1])

        if hasattr(self.ui, 'system_btn_log'):
            self.ui.system_btn_log.clicked.connect(self.open_log_file)

    def open_log_file(self):
        """Opens the application error log file (flowdeck_errors.log) in Notepad."""
        root_dir = PathManager.get_root_dir()
        log_path = os.path.join(root_dir, "logs", "flowdeck_errors.log")

        if os.path.exists(log_path):
            try:
                subprocess.Popen(["notepad.exe", log_path])
            except Exception as e:
                logger.error(
                    f"Failed to open error log file with Notepad: {e}")
                try:
                    os.startfile(log_path)
                except Exception as ex:
                    msg = QMessageBox(self.main_window)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle(_("set_msg_title_error", "Error"))
                    msg.setText(
                        _("set_err_open_log", "Could not open log file:\n{error}").format(error=ex))
                    msg.setStyleSheet(self.get_msg_style())
                    msg.exec_()
        else:
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(_("set_msg_title_warning", "Warning"))
            msg.setText(_("set_warn_no_log_file",
                        "The error log file does not exist yet on disk."))
            msg.setStyleSheet(self.get_msg_style())
            msg.exec_()

    def get_msg_style(self):
        """Returns stylesheet based on active theme."""
        theme = self.config.get("theme", "Modern Dark")
        return DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE

    def setup_ui(self):
        """Binds UI elements to controller methods."""
        if hasattr(self.ui, 'combo_themeSelect'):
            self.ui.combo_themeSelect.clear()
            self.ui.combo_themeSelect.addItems(["Modern Dark", "Modern Light"])

        if hasattr(self.ui, 'combo_languageSelect'):
            self.ui.combo_languageSelect.clear()
            self.ui.combo_languageSelect.addItem(
                _("set_lang_el", "Greek"), "Ελληνικά")
            self.ui.combo_languageSelect.addItem(
                _("set_lang_en", "English"), "English")

        if hasattr(self.ui, 'combo_updateFrequency'):
            self.ui.combo_updateFrequency.clear()
            self.ui.combo_updateFrequency.addItem(
                _("set_freq_startup", "On Startup"), "On Startup")
            self.ui.combo_updateFrequency.addItem(
                _("set_freq_daily", "Every 24 Hours"), "Every 24 Hours")
            self.ui.combo_updateFrequency.addItem(
                _("set_freq_manual", "Manual Only"), "Manual Only")

        if hasattr(self.ui, 'btn_browsePath'):
            self.ui.btn_browsePath.clicked.connect(self.browse_install_path)

        if hasattr(self.ui, 'btn_openPath'):
            self.ui.btn_openPath.clicked.connect(self.open_install_path)

        if hasattr(self.ui, 'btn_clearActivityLog'):
            self.ui.btn_clearActivityLog.clicked.connect(self.clear_logs)

        if hasattr(self.ui, 'btn_resetDefaults'):
            self.ui.btn_resetDefaults.clicked.connect(self.factory_reset)

        if hasattr(self.ui, 'btn_scanAndRepair'):
            self.ui.btn_scanAndRepair.clicked.connect(self.scan_and_repair)

        if hasattr(self.ui, 'btn_backupApps'):
            self.ui.btn_backupApps.clicked.connect(self.open_backup_wizard)

        if hasattr(self.ui, 'btn_saveSettings'):
            self.ui.btn_saveSettings.clicked.connect(self.save_settings)

        if hasattr(self.ui, 'btn_checkUpdatesNow'):
            self.ui.btn_checkUpdatesNow.clicked.connect(
                self.manual_update_check)

    def populate_ui(self):
        """Populates UI components with current configuration and locks path controls if running from USB."""
        # Dynamic check for USB mode
        is_usb = PathManager.is_usb_drive()

        if hasattr(self.ui, 'txt_installPath'):
            self.ui.txt_installPath.setText(
                self.config.get("install_path", ""))
            self.ui.txt_installPath.setEnabled(not is_usb)
            if is_usb:
                self.ui.txt_installPath.setToolTip(
                    _("set_path_disabled_usb", "Path selection is disabled in Portable (USB) mode."))
            else:
                self.ui.txt_installPath.setToolTip("")

        if hasattr(self.ui, 'btn_browsePath'):
            self.ui.btn_browsePath.setEnabled(not is_usb)

        if hasattr(self.ui, 'chk_startOnBoot'):
            self.ui.chk_startOnBoot.setChecked(
                self.config.get("start_on_boot", False))

        if hasattr(self.ui, 'chk_minimizeToTray'):
            self.ui.chk_minimizeToTray.setChecked(
                self.config.get("minimize_to_tray", False))

        if hasattr(self.ui, 'chk_updateToStart'):
            self.ui.chk_updateToStart.setChecked(
                self.config.get("update_to_start", True))

        if hasattr(self.ui, 'chk_enableSilentUpdater'):
            self.ui.chk_enableSilentUpdater.setChecked(
                self.config.get("silent_updater", True))

        if hasattr(self.ui, 'combo_themeSelect'):
            self.ui.combo_themeSelect.setCurrentText(
                self.config.get("theme", "Modern Dark"))

        if hasattr(self.ui, 'combo_languageSelect'):
            lang_index = self.ui.combo_languageSelect.findData(
                self.config.get("language", "Ελληνικά"))
            if lang_index >= 0:
                self.ui.combo_languageSelect.setCurrentIndex(lang_index)

        if hasattr(self.ui, 'combo_updateFrequency'):
            freq_index = self.ui.combo_updateFrequency.findData(
                self.config.get("update_freq", "On Startup"))
            if freq_index >= 0:
                self.ui.combo_updateFrequency.setCurrentIndex(freq_index)

        # Update system statistics in the UI
        self.update_system_stats()

    def browse_install_path(self):
        """Opens a directory selection dialog and checks if selected path is on a removable drive."""
        folder = QFileDialog.getExistingDirectory(
            self.main_window, _("set_browse_title", "Select Installation Directory"))

        if folder:
            # Normalize path slashes for consistent UI display
            clean_folder = os.path.normpath(folder).replace("\\", "/")

            # Check if selected directory is on a removable drive
            is_removable = PathManager.check_removable_drive(clean_folder)

            if is_removable:
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("set_msg_title_warning", "Warning"))
                msg.setText(_(
                    "set_path_removable_drive",
                    "Removable drives cannot be used for the installation folder. Please select a folder on a local drive."
                ))
                msg.setStyleSheet(self.get_msg_style())
                msg.exec_()
                return

            self.ui.txt_installPath.setText(clean_folder)

    def open_install_path(self):
        """Opens the installation folder in Windows File Explorer."""
        raw_folder_path = self.ui.txt_installPath.text().strip()
        folder_path = PathManager.to_absolute_path(raw_folder_path)

        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle(_("set_msg_title_error", "Error"))
                msg.setText(f"Could not open folder:\n{e}")

                if 'DIALOG_STYLE' in globals() or 'DIALOG_STYLE' in locals():
                    msg.setStyleSheet(self.get_msg_style())
                msg.exec_()
        else:
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(_("set_msg_title_warning", "Warning"))
            msg.setText("This folder does not exist on disk.")

            if 'DIALOG_STYLE' in globals() or 'DIALOG_STYLE' in locals():
                msg.setStyleSheet(self.get_msg_style())
            msg.exec_()

    def save_settings(self):
        """Synchronizes UI state to configuration file and applies changes globally."""
        new_path = self.ui.txt_installPath.text().strip()
        self.config["install_path"] = new_path
        self.config["start_on_boot"] = self.ui.chk_startOnBoot.isChecked()
        self.config["minimize_to_tray"] = self.ui.chk_minimizeToTray.isChecked()
        self.config["update_to_start"] = self.ui.chk_updateToStart.isChecked()
        if hasattr(self.ui, 'chk_enableSilentUpdater'):
            self.config["silent_updater"] = self.ui.chk_enableSilentUpdater.isChecked()

        self.config["theme"] = self.ui.combo_themeSelect.currentText()
        self.config["language"] = self.ui.combo_languageSelect.currentData()
        self.config["update_freq"] = self.ui.combo_updateFrequency.currentData()

        try:
            self.config.save()

            # Refresh UI controls to reflect saved state
            self.populate_ui()

            self.apply_start_on_boot(self.config.get("start_on_boot", False))

            from ui.main_window import apply_global_theme
            apply_global_theme(self.config["theme"])

            if hasattr(self.main_window, 'activity_manager'):
                self.main_window.activity_manager.refresh_ui()

            if hasattr(self.main_window, 'dashboard_controller'):
                self.main_window.dashboard_controller.refresh_dashboard()

            if hasattr(self.main_window, 'my_apps_controller'):
                self.main_window.my_apps_controller.refresh_data()

            msg_box = QMessageBox(self.main_window)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(_("set_msg_title_success", "Success"))
            msg_box.setText(
                _("set_msg_success_text", "Settings saved successfully!"))
            msg_box.setStyleSheet(self.get_msg_style())

            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setObjectName("primaryButton")

            msg_box.exec()

        except Exception as e:
            err_box = QMessageBox(self.main_window)
            err_box.setIcon(QMessageBox.Critical)
            err_box.setWindowTitle(_("set_msg_title_error", "Error"))
            err_box.setText(
                _("set_msg_error_text", "Failed to save settings:\n{error}").format(error=e))
            err_box.setStyleSheet(self.get_msg_style())
            err_box.exec()

    # ==========================================
    # MAINTENANCE
    # ==========================================

    def clear_logs(self):
        """Purges activity history and updates the UI."""
        try:
            if hasattr(self.main_window, 'activity_manager'):
                self.main_window.activity_manager.clear_history()

            msg_box = QMessageBox(self.main_window)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(_("set_msg_title_success", "Success"))
            msg_box.setText(
                _("set_log_clear_success", "🧹 Activity history cleared successfully!"))
            msg_box.setStyleSheet(self.get_msg_style())

            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setObjectName("primaryButton")

            msg_box.exec()

        except Exception as e:
            err_box = QMessageBox(self.main_window)
            err_box.setIcon(QMessageBox.Critical)
            err_box.setWindowTitle(_("set_msg_title_error", "Error"))
            err_box.setText(f"Failed to clear activity history:\n{e}")
            err_box.setStyleSheet(self.get_msg_style())
            err_box.exec()

    def apply_start_on_boot(self, enable):
        """Configures Windows registry for automatic startup."""
        if sys.platform != "win32":
            return

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "FlowDeck"

        if getattr(sys, 'frozen', False):
            app_path = f'"{sys.executable}"'
        else:
            app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 key_path, 0, winreg.KEY_SET_VALUE)

            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
                logger.info("FlowDeck added to startup.")
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    logger.info("FlowDeck removed from startup.")
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
        except Exception as e:
            logger.error(
                f"Error configuring startup registry key: {e}")

    def manual_update_check(self):
        """Triggers a manual update check with UI feedback."""
        if hasattr(self.main_window, 'update_manager'):
            self.main_window.update_manager.check_for_updates(manual=True)

    def scan_and_repair(self):
        """Executes maintenance engine and handles user interaction for new discoveries."""

        def handle_confirm_dialog(folder_name, guessed_name, guessed_version):
            """Callback for user confirmation when new applications are detected."""
            QApplication.restoreOverrideCursor()

            dialog = ScanConfirmDialog(
                folder_name, guessed_name, guessed_version, self.main_window)
            result = dialog.exec_()

            QApplication.setOverrideCursor(Qt.WaitCursor)

            if result == QDialog.Accepted:
                final_name, final_version = dialog.get_values()
                return True, final_name, final_version
            return False, "", ""

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # create and inject helper services so UI can reuse them or test them separately
        scanner = PortableScanner()
        renamer = FolderRenamer()
        repository = AppRepository(self.db)

        manager = MaintenanceManager(
            self.db, self.config, scanner=scanner, renamer=renamer, repository=repository)

        success, removed, added, error_msg = manager.execute_scan_and_repair(
            dialog_callback=handle_confirm_dialog)

        QApplication.restoreOverrideCursor()

        if not success:
            QMessageBox.critical(self.main_window, _(
                "set_msg_title_error", "Error"), f"Maintenance failed:\n{error_msg}")
            return

        if hasattr(self.main_window, 'my_apps_controller'):
            self.main_window.my_apps_controller.refresh_data()

        if hasattr(self.main_window, 'dashboard_controller') and hasattr(self.main_window.dashboard_controller, 'load_favorites'):
            self.main_window.dashboard_controller.load_favorites()

        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                "act_scan_repair_success",
                event_type="update",
                params={
                    "added_count": str(added),
                    "removed_count": str(removed)
                }
            )

        success_box = QMessageBox(self.main_window)
        success_box.setStyleSheet(self.get_msg_style())
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle(
            _("set_maintenance_finished", "Maintenance Complete"))

        result_text = _("set_maintenance_details",
                        "🧹 Maintenance completed safely!\n\n"
                        "• Database backup: Created successfully.\n"
                        "• Orphaned items removed: {removed}\n"
                        "• New portable applications detected: {added}").format(
                            removed=removed,
                            added=added
        )
        success_box.setText(result_text)
        ok_btn = success_box.button(QMessageBox.Ok)
        if ok_btn:
            ok_btn.setObjectName("primaryButton")
        success_box.exec_()

    def open_backup_wizard(self):
        """Launches the Backup & Restore Wizard."""
        controller = BackupWizardController(self.main_window, self.db)
        controller.open_wizard()

    def factory_reset(self):
        """Resets the application to factory defaults without requiring a restart."""
        logger.info("=== [DEBUG_RESET] Starting factory_reset execution ===")

        # 1. Ask for confirmation before performing factory reset
        title = _("set_factory_reset_title", "Factory Reset")
        confirm_msg = _(
            "set_factory_reset_confirm",
            "Are you sure you want to perform a factory reset?\n\nThis will delete all settings, the database, and the activity log. This action cannot be undone!"
        )

        try:
            from ui.dialogs.dialog_utils import ask_confirmation
            confirmed = ask_confirmation(self.main_window, title, confirm_msg)
        except Exception:
            msg = QMessageBox(self.main_window)
            msg.setWindowTitle(title)
            msg.setText(confirm_msg)
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet(self.get_msg_style())
            confirmed = (msg.exec_() == QMessageBox.Yes)

        if not confirmed:
            return

        # 2. Ask if the user also wants to delete the portable applications folder (install_path)
        apps_confirm_msg = _(
            "set_factory_reset_apps_confirm",
            "Would you also like to delete the folder containing your portable applications?\n\nWarning: This will permanently delete all your installed applications!"
        )

        try:
            from ui.dialogs.dialog_utils import ask_confirmation
            delete_apps = ask_confirmation(
                self.main_window, title, apps_confirm_msg)
        except Exception:
            msg = QMessageBox(self.main_window)
            msg.setWindowTitle(title)
            msg.setText(apps_confirm_msg)
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet(self.get_msg_style())
            delete_apps = (msg.exec_() == QMessageBox.Yes)

        # 3. Perform database ERASE using dynamic connection from DatabaseManager
        if self.db and hasattr(self.db, 'get_connection'):
            try:
                logger.debug(
                    "[DEBUG_RESET] Opening dynamic database connection for wiping...")
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()

                    # Wipe data from the specific core application tables
                    for table in ["apps", "categories", "activity_log", "favorites"]:
                        try:
                            cursor.execute(f"DELETE FROM {table};")
                            logger.debug(
                                f"[DEBUG_RESET] Table {table} wiped successfully.")
                        except Exception as e_tbl:
                            logger.warning(
                                f"[DEBUG_RESET] Table {table} wipe skipped/failed: {e_tbl}")

                    # Reset internal autoincrement counter
                    try:
                        cursor.execute("DELETE FROM sqlite_sequence;")
                    except Exception:
                        pass

                    # Commit changes safely
                    conn.commit()

                    # Run VACUUM to reclaim space and flush the file
                    try:
                        cursor.execute("VACUUM;")
                        logger.debug("[DEBUG_RESET] Database VACUUM complete.")
                    except Exception as e_vac:
                        logger.warning(
                            f"[DEBUG_RESET] VACUUM skipped: {e_vac}")

                logger.debug(
                    "[DEBUG_RESET] Database clear block successfully finished.")
            except Exception as e:
                logger.error(f"[DEBUG_RESET] ERROR during database wipe: {e}")

        # 4. Perform settings rewrite with default parameters (No File Deletion)
        try:
            logger.debug(
                "[DEBUG_RESET] Resetting config.json to factory defaults.")
            self.config.reset_defaults()
            logger.debug(
                "[DEBUG_RESET] config.json successfully reset to defaults.")
        except Exception as e_cfg:
            logger.error(f"[DEBUG_RESET] ERROR resetting config file: {e_cfg}")

        # 5. Perform activity log file deletion
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.clear_history()
            logger.info(
                "[DEBUG_RESET] Activity log file deleted successfully")
        else:
            logger.warning(
                "[DEBUG_RESET] Activity manager not found; skipping activity log deletion.")

        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                "set_factory_reset_title", event_type="reset")

        # 6. Handle optional apps directory deletion
        apps_root = self.config.get("install_path")
        if delete_apps and apps_root and os.path.exists(apps_root) and os.path.isdir(apps_root):
            def remove_readonly(func, path, excinfo):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            try:
                shutil.rmtree(apps_root, onerror=remove_readonly)
                logger.info(
                    "[DEBUG_RESET] Apps folder tree deleted successfully.")

                # Re-create the empty apps folder just in case to keep paths clean
                os.makedirs(apps_root, exist_ok=True)
            except Exception as e:
                logger.error(
                    f"[DEBUG_RESET] ERROR deleting apps root folder {apps_root}: {e}")

        # 7. Apply global theme reset and update all active UI modules immediately
        try:
            logger.debug(
                "[DEBUG_RESET] Updating active UI controllers with default parameters...")

            # Apply default theme (Modern Dark) globally
            from ui.main_window import apply_global_theme
            apply_global_theme(self.config["theme"])

            # Configure registry boot setting to False
            self.apply_start_on_boot(False)

            # Re-populate current settings page elements (checkboxes, dropdowns)
            self.populate_ui()

            # Refresh other active UI views if they exist
            if hasattr(self.main_window, 'activity_manager'):
                self.main_window.activity_manager.refresh_ui()

            if hasattr(self.main_window, 'dashboard_controller'):
                self.main_window.dashboard_controller.refresh_dashboard()

            if hasattr(self.main_window, 'my_apps_controller'):
                self.main_window.my_apps_controller.refresh_data()

            logger.debug(
                "[DEBUG_RESET] All active UI views refreshed successfully.")
        except Exception as e_ui:
            logger.warning(f"[DEBUG_RESET] UI dynamic refresh warning: {e_ui}")

        # 8. Show success message box
        success_title = _("set_factory_reset_success_title", "Reset Complete")
        success_msg = _(
            "set_factory_reset_success_msg",
            "Factory reset completed successfully! All settings and data have been restored to default values."
        )

        success_box = QMessageBox(self.main_window)
        success_box.setStyleSheet(self.get_msg_style())
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle(success_title)
        success_box.setText(success_msg)
        ok_btn = success_box.button(
            QMessageBox.Ok) or success_box.addButton(QMessageBox.Ok)
        if ok_btn:
            ok_btn.setObjectName("primaryButton")
        success_box.exec_()
        logger.info(
            "=== [DEBUG_RESET] Factory Reset finished successfully! ===")
