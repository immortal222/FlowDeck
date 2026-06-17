import json
import logging
import socket
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox

from core.services.update_worker import UpdateCheckWorker
from locales.localization import _
from ui.dialogs.dialog_utils import create_styled_msgbox

logger = logging.getLogger(__name__)


class UpdateManager(QObject):
    """Coordinates background update checks and user notifications."""

    def __init__(self, main_window, db):
        super().__init__()
        self.main_window = main_window
        self.db = db
        self.is_manual_check = False
        self.update_worker = None
        self.updates_found = 0
        self._apps_cache = []  # Cache for faster version comparison

    def automatic_check_on_startup(self, config, settings_controller):
        """Executes automatic checks based on configured frequency."""
        # Background check logic depends on frequency settings

        frequency = config.get("update_freq", "On Startup")

        if frequency == "Manual Only" or frequency == "Χειροκίνητα":
            logger.info(
                "Update frequency set to Manual. Skipping startup check.")
            return

        elif frequency == "On Startup" or frequency == "Κάθε εκκίνηση":
            logger.info("Update frequency set to Each Boot. Starting check...")
            self.check_for_updates(manual=False)
            self._save_last_check_time(settings_controller)

        elif frequency == "Every 24 Hours" or frequency == "Κάθε 24 ώρες":
            last_check_str = config.get("last_update_check", "")

            if last_check_str:
                try:
                    last_check_time = datetime.fromisoformat(last_check_str)
                    if datetime.now() >= last_check_time + timedelta(hours=24):
                        logger.info(
                            "24 hours have passed since last check. Starting check...")
                        self.check_for_updates(manual=False)
                        self._save_last_check_time(settings_controller)
                    else:
                        logger.info(
                            "24 hours have not passed yet. Skipping update check.")
                except Exception as e:
                    logger.error(
                        f"Error parsing last_update_check timestamp: {e}")
                    self.check_for_updates(manual=False)
                    self._save_last_check_time(settings_controller)
            else:
                logger.info(
                    "No previous check timestamp found. Starting first check...")
                self.check_for_updates(manual=False)
                self._save_last_check_time(settings_controller)

    def _save_last_check_time(self, settings_controller):
        """Helper function to persist the last check timestamp in config.json."""
        try:
            settings_controller.config["last_update_check"] = datetime.now(
            ).isoformat()
            with open(settings_controller.config_file, "w", encoding="utf-8") as f:
                json.dump(settings_controller.config, f,
                          indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save last update check timestamp: {e}")

    def check_for_updates(self, manual=False):
        """Starts the update check with network connectivity validation."""
        self.is_manual_check = manual
        self.updates_found = 0
        apps_list = self.db.get_all_apps()

        # Log check event to activity timeline
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                "log_update_check", event_type="update")

        if not apps_list:
            if self.is_manual_check:
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
            return

        # Network Safety: Verify active internet connection
        try:
            # Fast connection attempt to Google DNS
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                ("8.8.8.8", 53))
            logger.info(
                "Internet connection detected. Proceeding with update check.")
        except (socket.error, Exception):
            logger.warning(
                "No internet connection. Update check aborted to protect local database.")

            # Αν ο έλεγχος πατήθηκε χειροκίνητα, ενημερώνουμε τον χρήστη
            if self.is_manual_check:
                msg = create_styled_msgbox(
                    self.main_window,
                    _("upd_title_error", "Network Error"),
                    _("upd_no_internet_text",
                      "No internet connection detected.\nPlease check your connection and try again."),
                    is_warning=True
                )
                msg.setStandardButtons(QMessageBox.Ok)
                ok_button = msg.button(QMessageBox.Ok)
                if ok_button:
                    ok_button.setObjectName("primaryButton")
                msg.exec_()

            self.is_manual_check = False
            return

        # Populate cache for update comparison
        self._apps_cache = apps_list
        self.update_worker = UpdateCheckWorker(apps_list, self.db)

        # Connect signals
        self.update_worker.app_checked.connect(self.track_updates)
        self.update_worker.finished.connect(self.on_check_finished)
        self.update_worker.start()

    def track_updates(self, name, has_update, latest_ver):
        """Monitors worker results and increments update counter."""
        # Use cache to avoid redundant database queries
        for app in self._apps_cache:
            # Case-insensitive name resolution
            if str(app.get("name")).lower() == str(name).lower():
                # Normalize current and latest versions for comparison
                current = str(app.get("current_version", app.get(
                    "ver", "1.0"))).strip().lower().lstrip('v')

                if not latest_ver:
                    logger.debug(
                        f"No latest version info for {name}, skipping.")
                    break

                latest = str(latest_ver).strip().lower().lstrip('v')

                logger.debug(
                    f"Comparing {name}: Current v{current} vs Latest v{latest}")

                # Prevent false positives on empty or unknown versions
                if current != latest and latest not in ["", "none", "unknown"]:
                    self.updates_found += 1
                    logger.info(f"UPDATE FOUND for {name}!")
                break

    def on_check_finished(self):
        """Cleanup and UI notification upon thread completion."""
        if hasattr(self.main_window, 'my_apps_controller'):
            self.main_window.my_apps_controller.refresh_data()

        # Determine notification visibility based on user preference
        is_silent = True
        if hasattr(self.main_window, 'settings_controller'):
            is_silent = self.main_window.settings_controller.config.get(
                "silent_updater", True)

        # Show dialog for manual checks or if silent mode is off and updates were found
        if self.is_manual_check or (not is_silent and self.updates_found > 0):
            title = _("upd_title_success", "Update Check")
            if self.updates_found > 0:
                text = _("upd_found_text", "Update check complete! Found {count} updates.").format(
                    count=self.updates_found)
            else:
                text = _("upd_not_found_text",
                         "Update check complete! All applications are up to date.")

            msg = create_styled_msgbox(
                self.main_window, title, text, is_warning=False)

            ok_button = msg.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setObjectName("primaryButton")

            msg.exec_()

        # Reset state
        self._apps_cache = []
        self.is_manual_check = False
