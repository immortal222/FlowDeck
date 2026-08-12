import logging
import socket
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox

from core.services.update_worker import UpdateCheckWorker
from locales.localization import _
from ui.dialogs.dialog_utils import create_styled_msgbox
from core.utils import update_all_ini_files

logger = logging.getLogger(__name__)


class UpdateManager(QObject):
    """Coordinates background and manual update checks with clear separation of concerns.

    Responsibilities:
    1. Fetch application metadata from the database
    2. Validate network connectivity before performing update checks
    3. Start the worker that retrieves online version metadata
    4. Notify UI / refresh application views after completion
    5. Track background vs manual check behavior separately
    """

    def __init__(self, main_window, db):
        super().__init__()
        self.main_window = main_window
        self.db = db
        self.is_manual_check = False
        self.update_worker = None
        self.updates_found = 0
        self._apps_cache = []
        self.last_check_time = None
        self.status = "idle"
        self.last_check_summary = ""

    @property
    def portable_root(self):
        if hasattr(self.main_window, "settings_controller"):
            return self.main_window.settings_controller.config.get("install_path")
        return None

    def automatic_check_on_startup(self, config, settings_controller):
        """Executes automatic checks based on configured frequency."""
        frequency = config.get("update_freq", "On Startup")

        if frequency in ("Manual Only", "Χειροκίνητα"):
            logger.info(
                "Update frequency set to Manual. Skipping startup check.")
            return

        if frequency in ("On Startup", "Κάθε εκκίνηση"):
            logger.info("Update frequency set to Each Boot. Starting check...")
            self.check_for_updates(manual=False)
            self._save_last_check_time(settings_controller)
            return

        if frequency in ("Every 24 Hours", "Κάθε 24 ώρες"):
            if self._should_run_24h_check(config):
                logger.info(
                    "24 hours have passed since last check. Starting check...")
                self.check_for_updates(manual=False)
                self._save_last_check_time(settings_controller)
            else:
                logger.info(
                    "24 hours have not passed yet. Skipping update check.")

    def _should_run_24h_check(self, config):
        last_check_str = config.get("last_update_check", "")
        if not last_check_str:
            logger.info(
                "No previous check timestamp found. Starting first check...")
            return True

        try:
            last_check_time = datetime.fromisoformat(last_check_str)
            return datetime.now() >= last_check_time + timedelta(hours=24)
        except Exception as e:
            logger.error(f"Error parsing last_update_check timestamp: {e}")
            return True

    def _save_last_check_time(self, settings_controller):
        """Persist the last update check timestamp in config.json."""
        try:
            settings_controller.config["last_update_check"] = datetime.now(
            ).isoformat()
            settings_controller.config.save()
        except Exception as e:
            logger.error(f"Failed to save last update check timestamp: {e}")

    def check_for_updates(self, manual=False):
        """Starts the update check process, manual or background."""
        self.is_manual_check = manual
        self.updates_found = 0
        self._apps_cache = []
        self.status = "checking"
        self.last_check_time = datetime.now()
        self.last_check_summary = ""

        update_all_ini_files(self.portable_root, self.db)

        apps_list = self._get_installed_apps()
        self._log_update_check()

        if not apps_list:
            self._notify_no_apps_found()
            self.status = "idle"
            return

        if not self._has_network_connection():
            self._notify_network_missing()
            self.status = "idle"
            self.is_manual_check = False
            return

        self._apps_cache = apps_list
        self._start_worker(apps_list)

    def _get_installed_apps(self):
        try:
            return self.db.get_all_apps()
        except Exception as e:
            logger.error(f"Error reading installed apps from database: {e}")
            return []

    def _log_update_check(self):
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                "log_update_check", event_type="update")

    def _has_network_connection(self):
        try:
            socket.setdefaulttimeout(2)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            logger.info(
                "Internet connection detected. Proceeding with update check.")
            return True
        except Exception:
            logger.warning(
                "No internet connection. Update check aborted to protect local database.")
            return False

    def _notify_no_apps_found(self):
        if not self.is_manual_check:
            return

        msg = create_styled_msgbox(
            self.main_window,
            _("upd_title_warning", "Warning"),
            _("upd_no_apps", "No installed applications found in database."),
            is_warning=True
        )
        ok_button = msg.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setObjectName("primaryButton")
        msg.exec_()

    def _notify_network_missing(self):
        if not self.is_manual_check:
            return

        msg = create_styled_msgbox(
            self.main_window,
            _("upd_title_error", "Network Error"),
            _(
                "upd_no_internet_text",
                "No internet connection detected.\nPlease check your connection and try again."
            ),
            is_warning=True
        )
        msg.setStandardButtons(QMessageBox.Ok)
        ok_button = msg.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setObjectName("primaryButton")
        msg.exec_()

    def _start_worker(self, apps_list):
        self.update_worker = UpdateCheckWorker(apps_list, self.db)
        self.update_worker.app_checked.connect(self.track_updates)
        self.update_worker.finished.connect(self.on_check_finished)
        self.update_worker.start()

    def track_updates(self, update_result):
        """Monitors worker results and increments update counter."""
        name = update_result.get("name", "")
        has_update = update_result.get("has_update", False)
        latest_ver = update_result.get("latest_version")

        for app in self._apps_cache:
            if str(app.get("name")).lower() == str(name).lower():
                current = str(
                    app.get("current_version", app.get("ver", "1.0")))
                current = current.strip().lower().lstrip('v')

                if not latest_ver:
                    logger.debug(
                        f"No latest version info for {name}, skipping.")
                    break

                latest = str(latest_ver).strip().lower().lstrip('v')
                logger.debug(
                    f"Comparing {name}: Current v{current} vs Latest v{latest}")

                if has_update:
                    self.updates_found += 1
                    logger.info(f"UPDATE FOUND for {name}!")
                break

    def on_check_finished(self):
        """Cleanup and UI notification upon thread completion."""
        self.status = "completed"

        if hasattr(self.main_window, 'my_apps_controller'):
            self.main_window.my_apps_controller.refresh_data()

        self._show_completion_dialog()
        self._apps_cache = []
        self.is_manual_check = False

    def _show_completion_dialog(self):
        is_silent = True
        if hasattr(self.main_window, 'settings_controller'):
            is_silent = self.main_window.settings_controller.config.get(
                "silent_updater", True)

        if not self.is_manual_check and is_silent and self.updates_found == 0:
            return

        title = _("upd_title_success", "Update Check")
        if self.updates_found > 0:
            text = _(
                "upd_found_text",
                "Update check complete! Found {count} updates."
            ).format(count=self.updates_found)
        else:
            text = _(
                "upd_not_found_text",
                "Update check complete! All applications are up to date."
            )

        msg = create_styled_msgbox(
            self.main_window, title, text, is_warning=False)

        ok_button = msg.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setObjectName("primaryButton")
        msg.exec_()

    @property
    def has_pending_updates(self):
        return self.updates_found > 0
