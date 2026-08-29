# Standard Library Imports
import logging
import os
import sys

# Third-Party Library Imports
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QAction, QMainWindow, QMenu, QMessageBox,
                             QProgressDialog, QSystemTrayIcon)

# Local Application Imports
from core.services.activity_manager import ActivityManager
from core.services.config_manager import ConfigManager
from core.services.constants import GITHUB_REPO, GITHUB_USERNAME, VERSION
from core.services.database import DatabaseManager
from core.services.path_manager import PathManager
from core.services.update_manager import UpdateManager
from core.services.version_check import VersionCheckWorker
from core.services.version_update import UpdateDownloaderWorker
from locales.localization import _
from locales.ui_localizer import localize_main_window
from ui.generated.ui_main import Ui_MainWindow
from ui.pages.dashboard_page import DashboardController
from ui.pages.my_apps_page import MyAppsController
from ui.pages.settings_page import SettingsController
from ui.pages.wizard_window import WizardController
from ui.styles.styles import (ACTIVITY_THEMES, DIALOG_LIGHT_STYLE,
                              DIALOG_STYLE)

logger = logging.getLogger(__name__)


def apply_global_theme(theme_name):
    """Central function for applying the CSS theme globally."""
    theme_data = ACTIVITY_THEMES.get(
        theme_name, ACTIVITY_THEMES.get("Modern Dark"))
    base_style = theme_data["style"]
    arrow = theme_data["arrow"]

    # Get absolute path and normalize slashes for CSS
    path_to_arrow = PathManager.get_asset_path(arrow).replace("\\", "/")

    # NOTE: Add double quotes around the path
    final_style = base_style.replace("PLACEHOLDER_ARROW", f'"{path_to_arrow}"')

    app = QtWidgets.QApplication.instance()
    if app:
        app.setStyleSheet(final_style)
        main_window = app.activeWindow()
        if main_window:
            main_window.setWindowIcon(QtGui.QIcon(
                PathManager.get_asset_path("icons/FlowDeck.png")))
        for widget in app.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()


class AppMainWindow(QMainWindow):
    """Main portable application management app (formerly MyApp)."""

    def __init__(self, config_manager=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 1. Core Services
        self.db = DatabaseManager()

        # 2. Settings Loading
        self.config_manager = config_manager if config_manager is not None else ConfigManager()
        self.settings_controller = SettingsController(
            self, self.config_manager)

        # 3. Appearance & Theme
        icon_path = PathManager.get_asset_path("icons/FlowDeck.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Apply theme via central function to ensure properties like arrows load correctly
        user_theme = self.settings_controller.config.get(
            "theme", "Modern Dark")
        apply_global_theme(user_theme)

        self.setup_tray_icon()
        self.initialize_icons()

        # 4. Enable Localization
        localize_main_window(self)

        # 5. Create activity manager for Dashboard
        self.activity_manager = ActivityManager(self.config_manager)

        # 6. Sidebar Logic (Navigation)
        self.setup_sidebar_logic()

        # 7. Wizard Controller Connection (Modular Logic)
        self.wizard_controller = WizardController(self, self.ui, self.db)

        # 8. My Apps Page Controller initialization
        self.my_apps_controller = MyAppsController(self, self.ui, self.db)

        # 9. Dashboard Page Controller initialization
        self.dashboard_controller = DashboardController(
            self, self.ui, self.db, self.my_apps_controller.icon_provider)

        # 10. Default Page (Dashboard at startup)
        self.ui.contentStackedWidget.setCurrentWidget(self.ui.page_dashboard)

        # 11. Update Manager Initialization
        self.update_manager = UpdateManager(self, self.db)

        # self.update_manager.automatic_check_on_startup(
        #     self.settings_controller.config,
        #     self.settings_controller
        # )

        # 12. Check for GitHub updates if enabled
        self.check_for_github_updates()

        # 13. Check if we just updated and show message / log activity
        self.check_post_update_flag()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(
            PathManager.get_asset_path('icons/FlowDeck.png')))

        tray_menu = QMenu()

        show_action = QAction(_("tray_menu_show", "Εμφάνιση"), self)
        show_action.triggered.connect(self.showNormal)

        exit_action = QAction(_("tray_menu_exit", "Έξοδος"), self)
        exit_action.triggered.connect(self.force_close_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def force_close_app(self):
        """ Permanently closes the app from the Tray menu """
        self.is_force_closing = True  # Flag indicating manual exit
        if hasattr(self, 'db'):
            self.db.create_backup()
        QtWidgets.QApplication.quit()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self.restore_from_tray()

    def initialize_icons(self):
        """
        Initializes all UI icons using PathManager for dev and PyInstaller compatibility.
        """
        # Sidebar Navigation Icons
        self.ui.navIcon_Dashboard.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/home.png")))
        self.ui.navIcon_MyApps.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/apps.png")))
        self.ui.navIcon_Wizard.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/rocket.png")))
        self.ui.navIcon_Settings.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/settings.png")))

        # Ensure About icon loads correctly
        if hasattr(self.ui, 'navIcon_About'):
            self.ui.navIcon_About.setPixmap(QtGui.QPixmap(
                PathManager.get_asset_path("icons/info.png")))

        # Dashboard Icons
        self.ui.lblDash_TipIcon.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/lamp.png")))
        # Dynamic USB Mode Check
        if PathManager.is_usb_drive():
            self.ui.usbIcon.setPixmap(QtGui.QPixmap(
                PathManager.get_asset_path("icons/usb.png")))
            self.ui.usbIcon.setToolTip("Running in Portable Mode (USB)")
        else:
            self.ui.usbIcon.setPixmap(QtGui.QPixmap(
                PathManager.get_asset_path("icons/disk.png")))
            self.ui.usbIcon.setToolTip("Running in Local PC Mode")

        # Logo Icons
        self.ui.iconDash_Logo.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/FlowDeck.png")))
        self.ui.myApps_IconLogo.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/FlowDeck.png")))
        self.ui.wizard_IconLogo.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/FlowDeck.png")))

    def restore_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def check_for_github_updates(self, from_about_dialog=False):
        """Check for GitHub updates asynchronously if enabled in config"""
        try:
            if not from_about_dialog:
                update_to_start = self.settings_controller.config.get(
                    "update_to_start", False)
                if not update_to_start:
                    return

            self.from_about_dialog = from_about_dialog
            current_version = VERSION

            # Initialize and start background worker
            self.version_worker = VersionCheckWorker(
                username=GITHUB_USERNAME,
                repo=GITHUB_REPO,
                current_version=current_version,
                parent=self
            )
            self.version_worker.finished.connect(
                self._on_version_check_finished)
            self.version_worker.start()

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")

    def _on_version_check_finished(self, has_update, update_info, error_msg=None):
        """Handles the completion of the asynchronous version check."""
        if error_msg:
            # Show network/connection error popup if check failed
            if getattr(self, 'from_about_dialog', False):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("upd_title_error", "Network Error"))
                msg.setText(error_msg)
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()
            self.from_about_dialog = False
            return

        if has_update and update_info:
            # Show update prompt window
            self.show_update_dialog(update_info)
        else:
            # Show "No updates available" only if explicitly requested from About dialog and no errors occurred
            if getattr(self, 'from_about_dialog', False):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(
                    _("no_updates_title", "No Updates Available"))
                msg.setText(_("no_updates_text", "Your system is up to date."))
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()

        self.from_about_dialog = False

    def show_update_dialog(self, update_info):
        """Display update notification dialog with logic branch for compiled vs source code execution."""
        msg = QMessageBox(self)
        msg.setWindowTitle(_("upd_update_title", "Update Available"))
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)

        # Set icon
        icon_path = PathManager.get_asset_path("icons/FlowDeck.png")
        if os.path.exists(icon_path):
            msg.setIconPixmap(QtGui.QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Get version and build message details
        new_version = update_info.get("version", "Unknown")
        title = update_info.get("title", "New Release")
        changelog = update_info.get("changelog", "")
        html_url = update_info.get(
            "html_url", f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/releases")

        # Truncate changelog if too long
        if len(changelog) > 300:
            changelog = changelog[:300] + "..."

        # Check if running as compiled executable (sys.frozen) or from source code
        is_frozen = getattr(sys, 'frozen', False)

        if is_frozen:
            # Compiled Executable Mode (.exe)
            msg.setText(
                f"<h3>{_('upd_update_available', 'New Version Available')}</h3>"
                f"<p><b>{_('upd_new_version', 'New Version')}:</b> {new_version}</p>"
                f"<p><b>{_('upd_release_title', 'Release')}:</b> {title}</p>"
                f"<hr>"
                f"<p><b>{_('upd_changelog', 'Changelog')}:</b></p>"
                f"<p style='font-size: 10px; max-height: 100px; overflow-y: auto;'>{changelog}</p>"
                f"<hr>"
                f"<p>{_('upd_click_below', 'Click the button below to update FlowDeck.')}</p>"
            )

            update_button = msg.addButton(
                _("upd_update_button", "Update Now"), QMessageBox.AcceptRole)
            cancel_button = msg.addButton(
                _("upd_cancel_button", "Later"), QMessageBox.RejectRole)

            self.apply_dialog_theme(msg)
            result = msg.exec_()

            if result == QMessageBox.AcceptRole:
                self.start_update_download(update_info)
            else:
                # User chose "Later", proceed with apps check
                self.update_manager.automatic_check_on_startup(
                    self.settings_controller.config,
                    self.settings_controller
                )
        else:
            # Source Code / Development Mode
            msg.setText(
                f"<h3>{_('upd_update_available', 'New Version Available')} (Dev Mode)</h3>"
                f"<p><b>{_('upd_new_version', 'New Version')}:</b> {new_version}</p>"
                f"<p><b>{_('upd_release_title', 'Release')}:</b> {title}</p>"
                f"<hr>"
                f"<p><b>{_('upd_changelog', 'Changelog')}:</b></p>"
                f"<p style='font-size: 10px; max-height: 100px; overflow-y: auto;'>{changelog}</p>"
                f"<hr>"
                f"<p>{_('upd_source_mode_notice', 'You are running FlowDeck from source code. Please pull the latest changes from GitHub.')}</p>"
            )

            open_github_button = msg.addButton(
                _("upd_open_github_button", "Open Releases Page"), QMessageBox.AcceptRole)
            cancel_button = msg.addButton(
                _("upd_cancel_button", "Later"), QMessageBox.RejectRole)

            self.apply_dialog_theme(msg)
            result = msg.exec_()

            if result == QMessageBox.AcceptRole:
                # Open the releases page in the default web browser
                QDesktopServices.openUrl(QUrl(html_url))
            else:
                self.update_manager.automatic_check_on_startup(
                    self.settings_controller.config,
                    self.settings_controller
                )

    def start_update_download(self, update_info):
        """Initializes the download worker and displays the progress dialog."""
        download_url = update_info.get("download_url")
        digest = update_info.get("digest")
        new_version = update_info.get("version", "latest")

        if not download_url:
            QMessageBox.warning(self, "Error", "Download URL is missing.")
            return

        # Create Progress Dialog with Abort button
        self.progress_dialog = QProgressDialog(
            _("upd_progress_starting_download", "Starting download..."),
            _("upd_progress_abort_button", "Abort"),
            0,
            100,
            self
        )
        self.progress_dialog.setWindowTitle(
            _("upd_progress_window_title", "Downloading Update"))
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.apply_dialog_theme(self.progress_dialog)

        # Target directory and executable name
        target_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        exe_name = "FlowDeck.exe"

        # Initialize Background Worker Thread with new_version
        self.update_worker = UpdateDownloaderWorker(
            download_url, digest, target_dir, exe_name, new_version=new_version)

        # Connect signals
        self.update_worker.progress.connect(self.progress_dialog.setValue)
        self.update_worker.status_changed.connect(
            self.progress_dialog.setLabelText)
        self.update_worker.finished.connect(self.on_update_download_finished)

        # Connect Cancel button to worker
        self.progress_dialog.canceled.connect(self.update_worker.cancel)

        # Start execution
        self.progress_dialog.show()
        self.update_worker.start()

    def on_update_download_finished(self, success, message):
        """Handles the completion of the update download process."""
        self.progress_dialog.close()

        if success:
            # Execute updater.exe directly from the extracted temp directory
            extract_dir = message
            updater_exe = os.path.join(extract_dir, "updater.exe")
            config_json = os.path.join(extract_dir, "update_config.json")

            if os.path.exists(updater_exe) and os.path.exists(config_json):
                import subprocess
                subprocess.Popen([updater_exe, config_json], cwd=extract_dir)
                self.force_close_app()
            else:
                logger.error(
                    "updater.exe or update_config.json not found in the extracted package.")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle(_("upd_error_title", "Error"))
                msg.setText(_("upd_error_msg",
                              "updater.exe or update_config.json was not found in the extracted package."))
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()
        else:
            # Check if the process was explicitly cancelled by the user
            is_cancelled = getattr(self.update_worker, 'is_cancelled', False)

            if is_cancelled:
                # Show cancellation message directly without the failure header
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(_("upd_update_title", "Information"))
                msg.setText(message)
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()
            else:
                # Show error popup only for actual failures
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle(
                    _("upd_update_failed_title", "Update Failed"))
                msg.setText(
                    _("upd_update_failed_msg", "Update process failed:\n{error}").format(error=message))
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()

            # Proceed with apps check ONLY if the update process was NOT triggered manually from the About dialog
            if not getattr(self, 'from_about_dialog', False):
                self.update_manager.automatic_check_on_startup(
                    self.settings_controller.config,
                    self.settings_controller
                )

    def check_post_update_flag(self):
        """Checks for update_flag.json on startup, notifies user and logs activity."""
        flag_path = os.path.join(os.path.dirname(
            os.path.abspath(sys.argv[0])), "update_flag.json")
        if not os.path.exists(flag_path):
            return

        try:
            import json
            with open(flag_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("updated"):
                version_str = data.get("version", VERSION)

                # Show notification dialog
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(
                    _("upd_update_success_title", "Update Successful"))
                msg.setText(
                    _("upd_update_success_msg", "FlowDeck was successfully updated to version {version}.").format(version=version_str))
                msg.setStandardButtons(QMessageBox.Ok)
                self.apply_dialog_theme(msg)
                msg.exec_()

                # Log activity in Activity Log using the correct log() method
                if hasattr(self, 'activity_manager'):
                    self.activity_manager.log(
                        message_key="upd_log_update_success",
                        event_type="update",
                        params={"version": version_str}
                    )
        except Exception as e:
            logger.error(f"Error reading update_flag.json: {e}")
        finally:
            # Clean up flag file so dialog isn't repeated on subsequent launches
            if os.path.exists(flag_path):
                try:
                    os.remove(flag_path)
                except Exception as e:
                    logger.error(f"Failed to delete update_flag.json: {e}")

    def show_about_dialog(self):
        # Localized strings for the About dialog
        about_title = _("about_window_title", "About FlowDeck")
        about_desc = _("about_description",
                       "Portable application manager for Windows.")
        about_7z = _("about_7zip_mention",
                     "Includes 7-Zip (7za.exe) for archive management.")
        about_scoop = _("about_scoop_mention",
                        "Powered by the Scoop ecosystem for portable apps.")
        about_choco = _("about_chocolatey_mention",
                        "Supports Chocolatey for system package installations.")
        about_ver = _("about_version_label", "Version")
        about_license_lbl = _("about_license_label", "License")
        about_license_val = _("about_license_value", "GNU GPLv3")
        about_github = _("about_github", "GitHub")

        msg = QMessageBox(self)
        msg.setWindowTitle(about_title)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)

        # Load and set the FlowDeck icon for the About dialog
        icon_path = PathManager.get_asset_path("icons/FlowDeck.png")
        if os.path.exists(icon_path):
            msg.setIconPixmap(QtGui.QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        github_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"

        # Set the HTML content for the About dialog with localized strings
        msg.setText(
            f"<h2>FlowDeck</h2>"
            f"<p><b>{about_ver}:</b> {VERSION} &nbsp;&nbsp;|&nbsp;&nbsp; <b>{about_license_lbl}:</b> <span style='color: #41CD52;'>{about_license_val}</span></p>"
            f"<p>{about_desc}</p>"
            f"<hr>"
            f"<p style='font-size: 11px; line-height: 1.5; color: #a0a0a0;'>"
            f"• {about_scoop}<br>"
            f"• {about_choco}<br>"
            f"• {about_7z}"
            f"</p>"
            f"<hr>"
            f"<p><b>{about_github}:</b> <a href='{github_url}' style='color: #2371C4;'>{github_url}</a></p>"
            f"<p style='font-size: 10px; color: #777;'>© 2026 George Papadopoulos. Released under GNU GPLv3.</p>"
        )

        check_updates_button = msg.addButton(
            _("check_updates_button", "Check for Updates"),
            QMessageBox.ResetRole
        )

        ok_button = msg.addButton(
            QMessageBox.Ok
        )

        check_updates_button.clicked.connect(
            lambda _: self.check_for_github_updates(from_about_dialog=True)
        )

        self.apply_dialog_theme(msg)

        msg.exec()

    def setup_sidebar_logic(self):
        # 1. List of navigation frames
        self.nav_frames = [
            self.ui.navIconFrame_Dashboard,
            self.ui.navIconFrame_MyApps,
            self.ui.navIconFrame_Wizard,
            self.ui.navIconFrame_Settings
        ]

        # 2. Connect click events to frames
        for frame in self.nav_frames:
            frame.mousePressEvent = lambda event, f=frame: self.on_nav_item_clicked(
                f)

        # Connect About frame to dialog
        if hasattr(self.ui, 'navIconFrame_About'):
            self.ui.navIconFrame_About.mousePressEvent = lambda event: self.show_about_dialog()

        # Initial page selection
        self.on_nav_item_clicked(self.ui.navIconFrame_Dashboard)

    def on_nav_item_clicked(self, clicked_frame):
        # Set active state for menu frames
        for frame in self.nav_frames:
            if frame == clicked_frame:
                frame.setProperty("active", "true")
            else:
                frame.setProperty("active", "false")

            # Refresh style to show active state indicator
            frame.style().unpolish(frame)
            frame.style().polish(frame)

        # 3. Page change & Data refresh
        if clicked_frame == self.ui.navIconFrame_Dashboard:
            self.ui.contentStackedWidget.setCurrentIndex(0)

            # Refresh Dashboard data on access
            if hasattr(self, 'dashboard_controller'):
                self.dashboard_controller.refresh_dashboard()

        elif clicked_frame == self.ui.navIconFrame_Wizard:
            self.ui.contentStackedWidget.setCurrentIndex(1)

        elif clicked_frame == self.ui.navIconFrame_Settings:
            self.ui.contentStackedWidget.setCurrentIndex(2)

        elif clicked_frame == self.ui.navIconFrame_MyApps:
            self.ui.contentStackedWidget.setCurrentIndex(3)
            if hasattr(self, 'my_apps_controller'):
                self.my_apps_controller.refresh_data()

    def closeEvent(self, event):
        """ Handles window close event (Minimize to Tray logic) """
        # If force closing, allow exit
        if getattr(self, 'is_force_closing', False):
            event.accept()
            return

        # Read user setting (default: True)
        minimize_to_tray = True
        try:
            if hasattr(self, 'settings_controller') and hasattr(self.settings_controller, 'config'):
                raw_value = self.settings_controller.config.get(
                    "minimize_to_tray", True)

                # Convert potential string values to boolean
                if isinstance(raw_value, str):
                    minimize_to_tray = raw_value.lower() == 'true'
                else:
                    minimize_to_tray = bool(raw_value)
            else:
                logger.warning(
                    "settings_controller not found. Using default minimize_to_tray=True.")
        except Exception as e:
            logger.warning(
                f"Error reading minimize_to_tray: {e}")

        logger.debug(f"Final minimize_to_tray value: {minimize_to_tray}")

        # If enabled, hide window and ignore close event
        if minimize_to_tray and hasattr(self, 'tray_icon'):
            self.hide()
            self.tray_icon.showMessage(
                _("tray_title", "FlowDeck"),
                _("tray_message", "The application continues to run in the background."),
            )
            event.ignore()
        else:
            # Accept window close
            if hasattr(self, 'db'):
                self.db.create_backup()

            event.accept()
            # Remove tray icon and quit application
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            QtWidgets.QApplication.quit()

    def apply_dialog_theme(self, dialog):
        """Εφαρμόζει το κατάλληλο stylesheet σε ένα dialog με βάση το τρέχον theme."""
        current_theme = self.settings_controller.config.get(
            "theme", "Modern Dark")
        if current_theme == "Modern Light":
            dialog.setStyleSheet(DIALOG_LIGHT_STYLE)
        else:
            dialog.setStyleSheet(DIALOG_STYLE)
