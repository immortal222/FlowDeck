import os
import subprocess
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from core.services.path_manager import PathManager
from core.services.tips_manager import TipsManager
from core.utils import (get_disk_stats, get_folder_size_gb,
                        is_internet_available, is_update_available)
from locales.localization import _
from locales.ui_localizer import localize_dashboard_page
from ui.widgets.favorite_card import FavoriteCard


class DashboardController:
    """Manages the Dashboard page, displaying metrics, activity history, and favorite apps."""

    def __init__(self, main_window, ui, db, icon_provider):
        self.main_window = main_window
        self.ui = ui
        self.db = db
        self.icon_provider = icon_provider

        # Bind UI components from generated code
        self.scroll_area = self.ui.dash_favScrollContent
        self.container_widget = self.ui.scrollAreaWidgetContents
        self.fav_layout = self.ui.gridLayout_3

        # Configure layout spacing and margins
        self.fav_layout.setSpacing(15)
        self.fav_layout.setContentsMargins(10, 10, 10, 10)
        self.fav_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Connect activity log widget to global manager
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.set_ui_widget(
                self.ui.dash_activityLog)

        # Initialize and connect tips manager
        if hasattr(self.ui, 'lblDash_Tip'):
            self.tips_manager = TipsManager(self.ui.lblDash_Tip)
            self.tips_manager.load_and_render_tips()

        # Apply localization to static dashboard elements
        localize_dashboard_page(self)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Loads statistics and favorites from the database."""
        try:
            apps = self.db.get_all_apps()
        except Exception as e:
            print(f"⚠️ [DASHBOARD] Error loading data from database: {e}")
            return

        # Update application statistics and collect favorites
        favorites, total_apps, updates_count = self._update_app_info_stats(
            apps)

        # Update disk usage information
        self._update_disk_usage_stats()

        # Update date header
        self._update_date_header()

        # Update internet connectivity status
        is_online = is_internet_available()

        # Determine theme-specific icon prefix
        theme = "Modern Dark"
        if hasattr(self.main_window, 'settings_controller'):
            theme = self.main_window.settings_controller.config.get(
                "theme", "Modern Dark")
        prefix = "D" if theme == "Modern Dark" else ""

        if hasattr(self.ui, 'lblDash_StatusOnline'):
            self.ui.lblDash_StatusOnline.setText("")
            self.ui.lblDash_StatusOnline.setFixedSize(150, 50)
            self.ui.lblDash_StatusOnline.setAlignment(Qt.AlignCenter)

            status_type = "up" if is_online else "down"
            icon_name = f"icons/{prefix}connection_{status_type}.png"
            icon_path = PathManager.get_asset_path(
                icon_name).replace("\\", "/")

            self.ui.lblDash_StatusOnline.setPixmap(QPixmap(icon_path))
            self.ui.lblDash_StatusOnline.setScaledContents(True)

        # Render favorite application cards
        self._render_favorite_cards(favorites)

        # Refresh dashboard tips
        if hasattr(self, 'tips_manager'):
            self.tips_manager.load_and_render_tips()

    def _update_app_info_stats(self, apps):
        """Calculates application counts and updates, and retrieves favorites."""
        total_apps = 0
        updates_available = 0
        favorites = []

        for app in apps:
            total_apps += 1

            app_data = app if isinstance(app, dict) else {
                "id": app[0], "name": app[1], "local_path": app[2],
                "exe_path": app[3], "current_version": app[6] if len(app) > 6 else '1.0',
                "latest_version": app[7] if len(app) > 7 else (app[6] if len(app) > 6 else '1.0'),
                "is_favorite": app[8] if len(app) > 8 else 0
            }

            cur_ver = app_data.get('current_version', '1.0')
            lat_ver = app_data.get('latest_version', cur_ver)
            is_fav = app_data.get('is_favorite', 0)

            if is_update_available(cur_ver, lat_ver):
                updates_available += 1

            if is_fav == 1:
                favorites.append(app_data)

        if hasattr(self.ui, 'lblDash_StatAppsCount'):
            self.ui.lblDash_StatAppsCount.setText(str(total_apps))

        if hasattr(self.ui, 'lblDash_StatAppsSize') and hasattr(self.main_window, 'portable_root'):
            folder_size = get_folder_size_gb(
                self.main_window.portable_root)
            update_text = f"{updates_available} " + _(
                "dash_updates", "Updates") if updates_available > 0 else _("dash_up_to_date", "Up to Date")
            self.ui.lblDash_StatAppsSize.setText(
                f"{folder_size:.1f} GB | {update_text}")

        return favorites, total_apps, updates_available

    def _update_disk_usage_stats(self):
        """Calculates and displays disk usage statistics."""
        try:
            target_path = self.main_window.portable_root if hasattr(
                self.main_window, 'portable_root') else os.getcwd()
            stats = get_disk_stats(target_path)

            if hasattr(self.ui, 'lblDash_DiscSpaceSize'):
                self.ui.lblDash_DiscSpaceSize.setText(
                    f"{stats['used_gb']:.1f} GB / {stats['total_gb']:.1f} GB")

            if hasattr(self.ui, 'diskProgressBar'):
                self.ui.diskProgressBar.setValue(stats['percent_used'])
        except Exception as e:
            print(f"⚠️ [DASHBOARD] Failed to read disk usage: {e}")

    def _update_date_header(self):
        """Updates the date label in the header."""
        if hasattr(self.ui, 'lblDash_Date'):
            now = datetime.now()
            formatted_date = now.strftime("%A, %d %B %Y")
            self.ui.lblDash_Date.setText(formatted_date)

    def _render_favorite_cards(self, favorites):
        """Clears and re-renders favorite application cards."""
        self._clear_layout(self.fav_layout)

        row, col = 0, 0
        max_columns = 3

        for fav in favorites:
            card = FavoriteCard(
                fav,
                self.icon_provider,
                getattr(self.main_window, 'portable_root', ''),
                self.launch_app
            )
            self.fav_layout.addWidget(card, row, col)
            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    def launch_app(self, exe_path, dir_path, app_name):
        """Launches an application and logs the event."""
        print(f"DEBUG: Starting launch_app for {app_name}")

        if hasattr(self.main_window, 'activity_manager'):
            print("DEBUG: activity_manager found in main_window")

            if exe_path and os.path.exists(exe_path):
                dir_path = os.path.dirname(exe_path)
                try:
                    clean_env = os.environ.copy()

                    # Remove Qt-specific variables to prevent process conflicts
                    clean_env.pop("QT_PLUGIN_PATH", None)
                    clean_env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

                    # Execute application with a clean environment
                    subprocess.Popen(
                        [exe_path],
                        cwd=dir_path,
                        creationflags=0x00000008,
                        env=clean_env
                    )

                    self.main_window.activity_manager.log(
                        "act_launch_success",
                        event_type="launch",
                        params={"app_name": app_name}
                    )
                    print("DEBUG: Success logged successfully")

                except Exception as e:
                    print(f"DEBUG: Launch error (Exception): {e}")
                    self.main_window.activity_manager.log(
                        "act_launch_failed",
                        event_type="error",
                        params={"app_name": app_name}
                    )
            else:
                print(f"DEBUG: exe_path not found! (Was: {exe_path})")
                self.main_window.activity_manager.log(
                    "act_launch_not_found",
                    event_type="error",
                    params={"app_name": app_name}
                )
        else:
            print("DEBUG: WARNING! activity_manager not found. hasattr check failed.")

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
