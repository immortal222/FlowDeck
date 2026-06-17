import logging
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QAction, QMainWindow, QMenu, QMessageBox,
                             QSystemTrayIcon)

from core.services.activity_manager import ActivityManager
from core.services.database import DatabaseManager
from core.services.path_manager import PathManager
from core.services.update_manager import UpdateManager
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

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 1. Core Services
        self.db = DatabaseManager()

        # 2. Settings Loading
        self.settings_controller = SettingsController(self)

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
        self.activity_manager = ActivityManager()

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

        self.update_manager.automatic_check_on_startup(
            self.settings_controller.config,
            self.settings_controller
        )

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
        self.ui.usbIcon.setPixmap(QtGui.QPixmap(
            PathManager.get_asset_path("icons/disk.png")))

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

    def show_about_dialog(self):
        # Φόρτωση μεταφράσεων από το localization.py
        about_title = _("about_window_title", "About FlowDeck")
        about_desc = _("about_description", "Portable application manager for Windows.")
        about_7z = _("about_7zip_mention", "Includes 7-Zip (7za.exe) for archive management.")
        about_scoop = _("about_scoop_mention", "Powered by the Scoop ecosystem for portable apps.")
        about_choco = _("about_chocolatey_mention", "Supports Chocolatey for system package installations.")
        about_ver = _("about_version_label", "Version")
        about_license_lbl = _("about_license_label", "License")
        about_license_val = _("about_license_value", "GNU GPLv3")
        about_github = _("about_github", "GitHub")

        msg = QMessageBox(self)
        msg.setWindowTitle(about_title)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)

        # Φόρτωση εικονιδίου για ομοιομορφία
        icon_path = PathManager.get_asset_path("icons/FlowDeck.png")
        if os.path.exists(icon_path):
            msg.setIconPixmap(QtGui.QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        github_url = "https://github.com/immortal222/FlowDeck"
        
        # Διαμόρφωση του HTML κειμένου με τις αναφορές σε Scoop, Chocolatey και 7za
        msg.setText(
            f"<h2>FlowDeck</h2>"
        f"<p><b>{about_ver}:</b> 1.0.0 &nbsp;&nbsp;|&nbsp;&nbsp; <b>{about_license_lbl}:</b> <span style='color: #41CD52;'>{about_license_val}</span></p>"
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

        # Εφαρμογή στυλ ανάλογα με το τρέχον θέμα
        current_theme = self.settings_controller.config.get("theme", "Modern Dark")
        if current_theme == "Modern Light":
            msg.setStyleSheet(DIALOG_LIGHT_STYLE)
        else:
            msg.setStyleSheet(DIALOG_STYLE)

        # Ορισμός στυλ για το OK button
        ok_button = msg.addButton(QMessageBox.Ok)
        ok_button.setObjectName("primaryButton")

        msg.exec_()

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
                print(
                    "⚠️ [DEBUG] Δεν βρέθηκε το settings_controller. Χρησιμοποιείται η προεπιλογή (True).")
        except Exception as e:
            print(
                f"⚠️ [DEBUG] Σφάλμα κατά την ανάγνωση του minimize_to_tray: {e}")

        print(f"🛠️ [DEBUG] Τελική τιμή minimize_to_tray: {minimize_to_tray}")

        # If enabled, hide window and ignore close event
        if minimize_to_tray and hasattr(self, 'tray_icon'):
            self.hide()
            self.tray_icon.showMessage(
                _("tray_title", "FlowDeck"),
                _("tray_message", "Η εφαρμογή συνεχίζει να εκτελείται στο παρασκήνιο."),
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
