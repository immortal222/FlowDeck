from ui.widgets.favorite_card import FavoriteCard
from locales.ui_localizer import localize_dashboard_page
from locales.localization import _
import logging
import os
import subprocess
import traceback
from datetime import datetime

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from core.services.path_manager import PathManager
from core.services.tips_manager import TipsManager
from core.utils import (get_disk_stats, get_folder_size_gb,
                        is_internet_available, is_update_available)

logger = logging.getLogger(__name__)


def _write_trace(message):
    try:
        log_dir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'flowdeck_debug_trace.log'), 'a', encoding='utf-8') as handle:
            handle.write(message + '\n')
    except Exception:
        pass


class DashboardStatusWorker(QObject):
    """Computes dashboard status data off the UI thread."""

    status_ready = pyqtSignal(int, object, bool)

    def __init__(self, request_id, folder_path):
        super().__init__()
        self.request_id = request_id
        self.folder_path = folder_path

    def run(self):
        try:
            folder_size = None
            if self.folder_path:
                folder_size = get_folder_size_gb(self.folder_path)
            is_online = is_internet_available()
        except Exception as error:
            logger.error(
                f"[DASHBOARD] Background status refresh failed: {error}")
            folder_size = None
            is_online = False
        try:
            self.status_ready.emit(self.request_id, folder_size, is_online)
        except Exception as error:
            logger.error(f"[DASHBOARD] Failed to emit worker status: {error}")


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
        self._status_workers = {}
        self._status_request_id = 0
        self._cached_folder_size_gb = None
        self._cached_online_status = None
        self._updates_count = 0
        self._status_refresh_running = False

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
            self.tips_manager = TipsManager(
                self.ui.lblDash_Tip, self.main_window.config_manager)
            self.tips_manager.load_and_render_tips()

        # Apply localization to static dashboard elements
        localize_dashboard_page(self)
        self.refresh_dashboard()

    @property
    def portable_root(self):
        if not hasattr(self.main_window, 'settings_controller'):
            return ""
        install_path = self.main_window.settings_controller.config.get(
            "install_path", "")
        return os.path.normpath(install_path) if install_path else ""

    def _cleanup_status_worker(self, request_id):
        worker_data = self._status_workers.pop(request_id, None)
        if worker_data is None:
            return

        _, worker_thread = worker_data
        if worker_thread is not None and worker_thread.isRunning():
            try:
                worker_thread.quit()
                worker_thread.wait(500)
            except Exception:
                pass

    def _start_status_refresh(self):
        if self._status_refresh_running:
            return

        _write_trace("[DASHBOARD] start_status_refresh")
        folder_path = self.portable_root
        self._status_request_id += 1
        request_id = self._status_request_id

        worker_thread = QThread()
        worker = DashboardStatusWorker(request_id, folder_path)
        worker.moveToThread(worker_thread)
        worker.status_ready.connect(self._apply_status_refresh)
        worker_thread.started.connect(worker.run)
        worker_thread.start()

        self._status_workers[request_id] = (worker, worker_thread)
        self._status_refresh_running = True

    def _apply_status_refresh(self, request_id, folder_size, is_online):
        self._cleanup_status_worker(request_id)
        self._status_refresh_running = False

        if request_id != self._status_request_id:
            return

        self._cached_folder_size_gb = folder_size
        self._cached_online_status = is_online
        self._update_apps_size_label()
        self._update_online_status_icon()

    def _update_apps_size_label(self):
        if not hasattr(self.ui, 'lblDash_StatAppsSize'):
            return

        update_text = (
            f"{self._updates_count} " + _("dash_updates", "Updates")
            if self._updates_count > 0
            else _("dash_up_to_date", "Up to Date")
        )

        size_text = "..."
        if self._cached_folder_size_gb is not None:
            size_text = f"{self._cached_folder_size_gb:.1f} GB"

        self.ui.lblDash_StatAppsSize.setText(f"{size_text} | {update_text}")

    def _update_online_status_icon(self):
        if not hasattr(self.ui, 'lblDash_StatusOnline'):
            return

        theme = "Modern Dark"
        if hasattr(self.main_window, 'settings_controller'):
            theme = self.main_window.settings_controller.config.get(
                "theme", "Modern Dark")
        prefix = "D" if theme == "Modern Dark" else ""

        self.ui.lblDash_StatusOnline.setText("")
        self.ui.lblDash_StatusOnline.setFixedSize(150, 50)
        self.ui.lblDash_StatusOnline.setAlignment(Qt.AlignCenter)

        if self._cached_online_status is None:
            return

        status_type = "up" if self._cached_online_status else "down"
        icon_name = f"icons/{prefix}connection_{status_type}.png"
        icon_path = PathManager.get_asset_path(icon_name).replace("\\", "/")

        self.ui.lblDash_StatusOnline.setPixmap(QPixmap(icon_path))
        self.ui.lblDash_StatusOnline.setScaledContents(True)

    def refresh_dashboard(self):
        """Loads statistics and favorites from the database."""
        try:
            apps = self.db.get_all_apps()
        except Exception as e:
            logger.error(f"[DASHBOARD] Error loading data from database: {e}")
            return

        # Update application statistics and collect favorites
        favorites, total_apps, updates_count = self._update_app_info_stats(
            apps)
        self._updates_count = updates_count

        # Update disk usage information
        self._update_disk_usage_stats()

        # Update date header
        self._update_date_header()
        self._update_apps_size_label()
        self._update_online_status_icon()
        self._start_status_refresh()

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

        return favorites, total_apps, updates_available

    def _update_disk_usage_stats(self):
        """Calculates and displays disk usage statistics."""
        try:
            target_path = self.portable_root or os.getcwd()
            stats = get_disk_stats(target_path)

            if hasattr(self.ui, 'lblDash_DiscSpaceSize'):
                self.ui.lblDash_DiscSpaceSize.setText(
                    f"{stats['used_gb']:.1f} GB / {stats['total_gb']:.1f} GB")

            if hasattr(self.ui, 'diskProgressBar'):
                self.ui.diskProgressBar.setValue(stats['percent_used'])
        except Exception as e:
            logger.error(f"[DASHBOARD] Failed to read disk usage: {e}")

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
        logger.debug(f"Starting launch_app for {app_name}")

        if hasattr(self.main_window, 'activity_manager'):
            logger.debug("activity_manager found in main_window")

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
                    logger.debug("Success logged successfully")
                    if hasattr(self.db, 'increment_usage'):
                        self.db.increment_usage(app_name)

                except Exception as e:
                    logger.error(f"Launch error (Exception): {e}")
                    self.main_window.activity_manager.log(
                        "act_launch_failed",
                        event_type="error",
                        params={"app_name": app_name}
                    )
            else:
                logger.warning(f"exe_path not found! (Was: {exe_path})")
                self.main_window.activity_manager.log(
                    "act_launch_not_found",
                    event_type="error",
                    params={"app_name": app_name}
                )
        else:
            logger.warning("activity_manager not found. hasattr check failed.")

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
