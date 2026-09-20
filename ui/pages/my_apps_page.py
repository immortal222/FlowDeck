# Standard Library Imports
import logging
import os
import shutil
import subprocess
import traceback
import webbrowser

# Third-Party Library Imports
from PyQt5.QtCore import QFileInfo, QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileIconProvider,
                             QGridLayout, QMenu, QMessageBox, QProgressDialog)


# Local Module Imports
from core.services.path_manager import PathManager
from core.utils import get_folder_size_gb, is_update_available
from locales.localization import _
from locales.ui_localizer import localize_myapps_page
from ui.dialogs.dialog_utils import ask_confirmation, create_styled_msgbox
from ui.styles.styles import DIALOG_LIGHT_STYLE, DIALOG_STYLE
from ui.widgets.app_library_card import AppLibraryCard
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


"""
This file manages the "My Apps" page, displaying the list of installed applications, 
filtering, and providing management options.
"""


class FolderSizeWorker(QObject):
    """Calculates folder sizes in a worker thread to keep the UI responsive."""

    sizes_ready = pyqtSignal(int, dict)

    def __init__(self, request_id, folder_paths):
        super().__init__()
        self.request_id = request_id
        self.folder_paths = folder_paths

    def run(self):
        try:
            _write_trace(
                f"[MY_APPS] worker start request={self.request_id} dirs={len(self.folder_paths)}")
            results = {}
            for folder_path in self.folder_paths:
                normalized_path = os.path.normpath(folder_path)
                results[normalized_path] = get_folder_size_gb(normalized_path)
            _write_trace(
                f"[MY_APPS] worker complete request={self.request_id}")
            self.sizes_ready.emit(self.request_id, results)
        except Exception as error:
            logger.error(f"[MY_APPS] Folder size worker failed: {error}")
            _write_trace(
                f"[MY_APPS] worker exception request={self.request_id}: {error}\n{traceback.format_exc()}")
            try:
                self.sizes_ready.emit(self.request_id, {})
            except Exception as emit_error:
                _write_trace(
                    f"[MY_APPS] worker emit failed request={self.request_id}: {emit_error}")


class UninstallWorker(QThread):
    """Worker thread to delete application files with real-time byte progress reporting."""

    # Sends (deleted_bytes, total_bytes)
    progress_updated = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir

    def run(self):
        try:
            total_bytes = 0
            file_list = []

            # 1. Scan directory to calculate total byte size and build file list
            for root, dirs, files in os.walk(self.target_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        size = os.path.getsize(file_path)
                        total_bytes += size
                        file_list.append((file_path, size))
                    except Exception:
                        file_list.append((file_path, 0))

            deleted_bytes = 0

            # 2. Delete individual files and emit byte progress
            for file_path, size in file_list:
                try:
                    os.chmod(file_path, 0o777)
                    os.remove(file_path)
                except Exception:
                    pass
                deleted_bytes += size
                self.progress_updated.emit(deleted_bytes, total_bytes)

            # 3. Clean up remaining empty directory tree
            shutil.rmtree(self.target_dir, ignore_errors=True)

            self.finished_signal.emit(True, "")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class MyAppsController:
    """Central controller for the 'My Apps' library page."""

    def __init__(self, main_window, ui, db):
        self.main_window = main_window
        self.ui = ui
        self.db = db
        self.view_mode = "grid"

        self.cached_apps = []
        self.icon_cache = {}
        self.folder_size_cache = {}
        self.icon_provider = QFileIconProvider()
        self._apps_snapshot = None
        self._last_portable_root = None
        self._size_workers = {}
        self._size_request_id = 0
        self._size_load_pending = False

        # 1. Toolbar component connections
        if hasattr(self.ui, 'myApps_searchBox'):
            self.ui.myApps_searchBox.textChanged.connect(self.render_apps)

        if hasattr(self.ui, 'myApps_sortCombo'):
            # Localized sort option labels
            sort_update_label = _(
                "apps_ui_my_apps_sort_update", "Update Available")
            sort_favorite_label = _(
                "apps_ui_my_apps_sort_favorite", "Favorite")
            if self.ui.myApps_sortCombo.findText(sort_update_label) == -1:
                self.ui.myApps_sortCombo.addItem(sort_update_label)
            if self.ui.myApps_sortCombo.findText(sort_favorite_label) == -1:
                self.ui.myApps_sortCombo.addItem(sort_favorite_label)
            self.ui.myApps_sortCombo.currentIndexChanged.connect(
                self.render_apps)

        if hasattr(self.ui, 'myApps_viewBtn'):
            self.ui.myApps_viewBtn.clicked.connect(self.toggle_view_mode)

        # Connect global update manager to the update button
        if hasattr(self.ui, 'myApps_updateAllBtn'):
            self.ui.myApps_updateAllBtn.clicked.connect(
                lambda: self.main_window.update_manager.check_for_updates(
                    manual=True)
            )

        # Localize static UI elements
        localize_myapps_page(self)

        # 2. Initial data load
        self.refresh_data()

    @property
    def portable_root(self):
        """Always reads the current installation path from Settings."""
        return self.main_window.settings_controller.config.get("install_path")

    def toggle_view_mode(self):
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        self.ui.myApps_viewBtn.setText(f"View: {self.view_mode.title()}")
        self.render_apps()

    def get_safe_target_dir(self, db_folder_path, db_exe_path):
        target_dir = db_folder_path
        if not target_dir:
            if db_exe_path and os.path.exists(PathManager.to_absolute_path(db_exe_path)):
                target_dir = os.path.dirname(
                    PathManager.to_absolute_path(db_exe_path))
            else:
                return None

        # Resolve to an absolute path in memory
        target_dir = PathManager.to_absolute_path(target_dir)

        if hasattr(self.main_window, 'portable_root') and self.main_window.portable_root:
            root_norm = PathManager.to_absolute_path(
                self.main_window.portable_root)
            if target_dir == root_norm:
                return None

        return target_dir

    def _build_apps_snapshot(self, apps):
        snapshot = []
        for app in apps:
            if isinstance(app, dict):
                snapshot.append((
                    app.get('id'),
                    app.get('name'),
                    app.get('local_path'),
                    app.get('exe_path'),
                    app.get('current_version'),
                    app.get('latest_version'),
                    app.get('is_favorite', 0),
                ))
            else:
                snapshot.append((
                    app[0] if len(app) > 0 else None,
                    app[1] if len(app) > 1 else None,
                    app[2] if len(app) > 2 else None,
                    app[3] if len(app) > 3 else None,
                    app[6] if len(app) > 6 else None,
                    app[7] if len(app) > 7 else None,
                    app[8] if len(app) > 8 else 0,
                ))
        return tuple(snapshot)

    def _get_cached_folder_size(self, folder_path):
        if not folder_path:
            return 0.0

        normalized_path = os.path.normpath(folder_path)
        return self.folder_size_cache.get(normalized_path, 0.0)

    def _cleanup_size_worker(self, request_id):
        worker_data = self._size_workers.pop(request_id, None)
        if worker_data is None:
            return

        _, worker_thread = worker_data
        if worker_thread is not None and worker_thread.isRunning():
            try:
                worker_thread.quit()
                worker_thread.wait(500)
            except:
                pass

    def _start_size_loader(self, active_dirs):
        missing_dirs = [
            path for path in sorted(active_dirs)
            if path not in self.folder_size_cache
        ]

        self._size_load_pending = bool(missing_dirs)
        _write_trace(
            f"[MY_APPS] start_size_loader pending={bool(missing_dirs)} dirs={len(missing_dirs)}")
        if not missing_dirs:
            self.update_stats_label()
            return

        self._size_request_id += 1
        request_id = self._size_request_id
        worker_thread = QThread()
        worker = FolderSizeWorker(request_id, missing_dirs)
        worker.moveToThread(worker_thread)
        worker.sizes_ready.connect(self._apply_loaded_folder_sizes)
        worker_thread.started.connect(worker.run)
        worker_thread.start()

        self._size_workers[request_id] = (worker, worker_thread)

    def _apply_loaded_folder_sizes(self, request_id, size_map):
        try:
            _write_trace(
                f"[MY_APPS] apply_loaded_folder_sizes request={request_id}")
            self._cleanup_size_worker(request_id)

            if request_id != self._size_request_id:
                return

            self.folder_size_cache.update(size_map)
            self._size_load_pending = False

            for app in self.cached_apps:
                folder_path = app.get("dir")
                if not folder_path:
                    app["size_gb"] = 0.0
                    continue
                app["size_gb"] = self.folder_size_cache.get(
                    os.path.normpath(folder_path), 0.0)

            self.update_stats_label()
        except Exception as error:
            _write_trace(
                f"[MY_APPS] apply_loaded_folder_sizes exception: {error}\n{traceback.format_exc()}")
            logger.error(
                f"[MY_APPS] apply_loaded_folder_sizes failed: {error}")

    def update_stats_label(self):
        if not hasattr(self.ui, 'myApps_lblStats'):
            return

        total_gb = sum(a["size_gb"] for a in self.cached_apps)
        updates_count = sum(1 for a in self.cached_apps if a["has_update"])
        stats_text = (
            f"{len(self.cached_apps)} " + _("apps_installed", "Applications Installed") +
            f" | {total_gb:.2f} GB | {updates_count} " +
            _("apps_updates_avail", "Updates Available")
        )
        if self._size_load_pending:
            stats_text += " | " + _(
                "apps_calculating_size", "Calculating size...")

        self.ui.myApps_lblStats.setText(stats_text)

    def refresh_data(self):
        """Loads all application data from the database into memory."""
        try:
            apps = self.db.get_all_apps()
        except AttributeError:
            return

        # Get current installation root from settings
        current_root = ""
        if self.portable_root:
            current_root = os.path.normpath(self.portable_root)

        current_snapshot = self._build_apps_snapshot(apps)
        if (
            self.cached_apps
            and self._apps_snapshot == current_snapshot
            and self._last_portable_root == current_root
        ):
            self.render_apps()
            self._start_size_loader({
                os.path.normpath(app["dir"]) for app in self.cached_apps if app.get("dir")
            })
            return

        self.cached_apps = []
        self._apps_snapshot = current_snapshot
        self._last_portable_root = current_root
        active_dirs = set()

        for app in apps:
            if isinstance(app, dict):
                app_id = app.get('id', None)
                name = app.get('name', 'Unknown')
                db_folder = app.get('local_path', '')
                db_exe = app.get('exe_path', '')
                ver = app.get('current_version', '1.0')
                source = app.get('source', 'manual')
                update_url = app.get('update_url', '')
                homepage = app.get('homepage', '')
                db_latest_ver = app.get('latest_version', ver)
                is_favorite = app.get('is_favorite', 0)
            else:
                app_id = app[0] if len(app) > 0 else None
                name = app[1] if len(app) > 1 else 'Unknown'
                db_folder = app[2] if len(app) > 2 else ''
                db_exe = app[3] if len(app) > 3 else ''
                ver = app[6] if len(app) > 6 and app[6] else '1.0'
                source = app[4] if len(app) > 4 else 'manual'
                update_url = app[5] if len(app) > 5 else ''
                db_latest_ver = app[7] if len(app) > 7 and app[7] else ver
                is_favorite = app[8] if len(app) > 8 else 0

            if not db_exe:
                continue

            # Ensure absolute path for verification
            abs_exe_path = db_exe
            if not os.path.isabs(abs_exe_path):
                abs_exe_path = os.path.join(current_root, db_exe)

            abs_exe_path = os.path.normpath(abs_exe_path)

            # Verification 1: Does the executable exist on disk?
            if not os.path.exists(abs_exe_path):
                continue

            # Verification 2: Does it reside within the current installation root?
            try:
                norm_current = os.path.normpath(current_root)
                norm_exe = os.path.normpath(abs_exe_path)

                if os.path.commonpath([norm_current, norm_exe]) != norm_current:
                    continue
            except ValueError:
                continue

            safe_dir = self.get_safe_target_dir(db_folder, db_exe)
            if safe_dir:
                active_dirs.add(os.path.normpath(safe_dir))
            size_gb = self._get_cached_folder_size(safe_dir)

            # Check for version updates
            latest_ver = db_latest_ver  # Αν η βάση έχει NULL, αυτό θα γίνει None
            has_update = is_update_available(ver, latest_ver)

            if abs_exe_path not in self.icon_cache:
                self.icon_cache[abs_exe_path] = self.icon_provider.icon(
                    QFileInfo(abs_exe_path)).pixmap(48, 48)

            self.cached_apps.append({
                "id": app_id, "name": name, "dir": safe_dir, "exe": abs_exe_path,
                "ver": ver, "has_update": has_update, "latest_ver": latest_ver,
                "size_gb": size_gb, "source": source, "update_url": update_url,
                "homepage": homepage, "is_favorite": is_favorite
            })

        self.folder_size_cache = {
            path: size for path, size in self.folder_size_cache.items()
            if path in active_dirs
        }

        self.render_apps()
        self._start_size_loader(active_dirs)

    def render_apps(self):
        if self.ui.myApps_scrollContent.layout() is None:
            grid = QGridLayout(self.ui.myApps_scrollContent)
            grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        else:
            grid = self.ui.myApps_scrollContent.layout()
            while grid.count():
                item = grid.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    widget.setParent(None)
                    widget.deleteLater()
            QApplication.processEvents()

        display_apps = list(self.cached_apps)

        # Localized sort labels
        sort_az_label = _("apps_ui_my_apps_sort_az", "Name (A-Z)")
        sort_update_label = _(
            "apps_ui_my_apps_sort_update", "Update Available")
        sort_favorite_label = _("apps_ui_my_apps_sort_favorite", "Favorite")

        sort_mode = self.ui.myApps_sortCombo.currentText() if hasattr(
            self.ui, 'myApps_sortCombo') else sort_az_label
        if sort_mode == sort_az_label:
            display_apps.sort(key=lambda x: x["name"].lower())
        elif sort_mode == sort_update_label:
            display_apps.sort(key=lambda x: x["has_update"], reverse=True)
        elif sort_mode == sort_favorite_label:
            # Favorites first, then by name
            display_apps.sort(key=lambda x: (0 if x.get(
                "is_favorite", 0) else 1, x["name"].lower()))

        search_text = self.ui.myApps_searchBox.text().lower() if hasattr(self.ui,
                                                                         'myApps_searchBox') else ""
        if search_text:
            display_apps = [
                a for a in display_apps if search_text in a["name"].lower()]

        row, col = 0, 0
        max_cols = 3
        grid.setSpacing(20 if self.view_mode == "grid" else 12)

        for app in display_apps:
            card = AppLibraryCard(
                app,
                self.view_mode,
                self.icon_cache.get(app["exe"]),
                self.launch_app,
                self.show_options_menu,
                app.get("is_favorite", 0)
            )

            if self.view_mode == "grid":
                grid.addWidget(card, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            else:
                grid.addWidget(card, row, 0, 1, 3)
                row += 1

        self.update_stats_label()

    def launch_app(self, exe_path, app_name="Unknown"):
        """Opens the application and logs the activity."""
        if exe_path and os.path.exists(exe_path):
            dir_path = os.path.dirname(exe_path)
            try:
                # 1. Clone the Windows environment
                clean_env = os.environ.copy()

                # 2. Remove Qt-specific variables to avoid conflicts with child processes
                clean_env.pop("QT_PLUGIN_PATH", None)
                clean_env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

                # 3. Launch the application in a clean environment
                subprocess.Popen(
                    [exe_path],
                    cwd=dir_path,
                    creationflags=0x00000008,
                    env=clean_env
                )
                self.log_app_activity("act_launch_success", "launch", app_name)
                if hasattr(self.db, 'increment_usage'):
                    self.db.increment_usage(app_name)
            except OSError as e:
                # Handle WinError 740: The requested operation requires elevation
                if getattr(e, 'winerror', None) == 740:
                    try:
                        os.startfile(exe_path, 'runas')
                        self.log_app_activity(
                            "act_launch_success", "launch", app_name)
                    except Exception as runas_error:
                        logger.error(
                            f"Error launching elevated app {app_name}: {runas_error}")
                        self.log_app_activity(
                            "act_launch_failed", "error", app_name)
                else:
                    logger.error(f"Error launching app {app_name}: {e}")
                    self.log_app_activity(
                        "act_launch_failed", "error", app_name)
            except Exception as e:
                logger.error(f"Error launching app {app_name}: {e}")
                self.log_app_activity("act_launch_failed", "error", app_name)

    def uninstall_app(self, app):
        """Uninstalls the selected application, showing byte progress and removing shortcuts."""
        if ask_confirmation(
            self.main_window,
            _("apps_uninstall_confirm_title", "Confirm Removal"),
            _("apps_uninstall_confirm_text",
              "Are you sure you want to completely uninstall {app_name}?\nAll application data will be permanently deleted.").format(app_name=app['name'])
        ):
            target_dir = app["dir"]
            if not target_dir or target_dir == getattr(self.main_window, 'portable_root', ''):
                create_styled_msgbox(
                    self.main_window,
                    _("apps_security_error_title", "Security Error"),
                    _("apps_security_error_text", "Cancelled: The application folder could not be safely located.")).exec_()
                return

            # Initialize non-cancelable Progress Dialog with active theme styling
            progress = QProgressDialog(
                _("apps_uninstall_progress_label", "Uninstalling {app_name}...").format(app_name=app['name']), None, 0, 100, self.main_window)
            progress.setWindowModality(Qt.WindowModal)

            # Apply dynamic theme stylesheet matching application dialogs
            theme = self.main_window.settings_controller.config.get(
                "theme", "Modern Dark")
            progress_style = DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE
            progress.setStyleSheet(progress_style)

            progress.show()

            self.uninstall_worker = UninstallWorker(target_dir)

            def update_progress(deleted, total):
                if total > 0:
                    percent = int((deleted / total) * 100)
                    deleted_mb = deleted / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    progress.setLabelText(
                        _("apps_uninstall_deleting_files",
                          "Deleting files: {deleted_mb:.1f} MB / {total_mb:.1f} MB").format(
                            deleted_mb=deleted_mb, total_mb=total_mb)
                    )
                    progress.setValue(percent)

            def on_finished(success, error_msg):
                progress.close()

                # Remove shortcut (.lnk) from __Apps__ folder if it exists
                if hasattr(self, 'portable_root') and self.portable_root:
                    shortcut_path = os.path.join(
                        self.portable_root, "__Apps__", f"{app['name']}.lnk")
                    if os.path.exists(shortcut_path):
                        try:
                            os.remove(shortcut_path)
                            logger.info(f"Deleted shortcut: {shortcut_path}")
                        except Exception as err:
                            logger.warning(
                                f"Failed to delete shortcut {shortcut_path}: {err}")

                if success:
                    if hasattr(self.db, 'delete_app'):
                        self.db.delete_app(app["name"])
                    self.refresh_data()
                    if hasattr(self.main_window, 'activity_manager'):
                        self.log_app_activity(
                            "act_uninstalled_app", "error", app.get('name'))

                    create_styled_msgbox(
                        self.main_window,
                        _("apps_uninstall_success_title", "Success"),
                        _("apps_uninstall_success_text", "The application {app_name} was successfully removed!").format(app_name=app['name'])).exec_()
                else:
                    create_styled_msgbox(
                        self.main_window,
                        _("apps_uninstall_fail_title", "Error"),
                        _("apps_uninstall_fail_text", "Failed to uninstall: {error_msg}").format(error_msg=error_msg)).exec_()

            self.uninstall_worker.progress_updated.connect(update_progress)
            self.uninstall_worker.finished_signal.connect(on_finished)
            self.uninstall_worker.start()

    def show_options_menu(self, app):
        menu = QMenu(self.main_window)

        # Dynamic menu styling based on active theme
        current_theme = self.main_window.settings_controller.config.get(
            "theme", "Modern Dark")
        if current_theme == "Modern Light":
            style = """
                QMenu { background-color: #FFFFFF; color: #1A1A1A; border: 1px solid #CCCCCC; font-size: 13px; }
                QMenu::item { padding: 8px 30px; }
                QMenu::item:selected { background-color: #2B9099; color: white; }
            """
        else:
            style = """
                QMenu { background-color: #1A1A1A; color: #DBE5EB; border: 1px solid #474747; font-size: 13px; }
                QMenu::item { padding: 8px 30px; }
                QMenu::item:selected { background-color: #2371C4; color: white; }
            """
        menu.setStyleSheet(style)

        act_open = QAction(
            "🚀 " + _("apps_open", "Open Application"), self.main_window)
        act_open.triggered.connect(lambda _, p=app["exe"], n=app.get(
            "name", "Unknown"): self.launch_app(p, n))
        menu.addAction(act_open)

        app_folder = app.get("dir", None)
        if not app_folder or not os.path.exists(app_folder):
            exe_p = app.get("exe", "")
            if exe_p:
                if not os.path.isabs(exe_p) and hasattr(self.main_window, 'portable_root'):
                    exe_p = os.path.join(self.main_window.portable_root, exe_p)
                if os.path.exists(exe_p):
                    app_folder = os.path.dirname(exe_p)
        if app_folder and not os.path.isabs(app_folder) and hasattr(self.main_window, 'portable_root'):
            app_folder = os.path.join(
                self.main_window.portable_root, app_folder)
        if app_folder:
            app_folder = os.path.normpath(app_folder)

        act_folder = QAction(
            "📂 " + _("apps_open_folder", "Open Folder"), self.main_window)
        act_folder.triggered.connect(lambda checked, d=app_folder: os.startfile(d) if d and os.path.exists(
            d) else QMessageBox.critical(self.main_window, _("apps_folder_error_title", "Error"), _("apps_folder_error_text", "Folder not found or invalid:\n{folder_path}").format(folder_path=d)))
        menu.addAction(act_folder)

        homepage_url = app.get("homepage", "")
        if homepage_url:
            act_site = QAction(
                "🌐 " + _("apps_go_to_site", "Go to Site"), self.main_window)
            act_site.triggered.connect(
                lambda _, url=homepage_url: webbrowser.open(url))
            menu.addAction(act_site)

        # Single app update check via Global Manager
        act_check = QAction("🔄 " + _("apps_check_update",
                            "Check for Update"), self.main_window)
        act_check.triggered.connect(
            lambda: self.main_window.update_manager.check_for_updates(
                manual=True)
        )
        menu.addAction(act_check)

        # Dynamic Favorite toggle
        is_fav = app.get("is_favorite", 0)
        app_name = app.get("name", "Unknown")

        if is_fav:
            fav_text = "⭐ " + _("apps_favorite_remove",
                                "Remove from Favorites")
        else:
            fav_text = "⭐ " + _("apps_favorite", "Add to Favorites")

        act_favorite = QAction(fav_text, self.main_window)

        act_favorite.triggered.connect(
            lambda checked, a_id=app.get(
                "id"), c_status=is_fav, n=app_name: self.toggle_app_favorite(a_id, c_status, n)
        )
        menu.addAction(act_favorite)

        act_edit = QAction(
            "🔧 " + _("apps_edit_repair", "Edit & Repair"), self.main_window)
        act_edit.triggered.connect(lambda: self.open_edit_dialog(app))
        menu.addAction(act_edit)

        menu.addSeparator()

        act_uninstall = QAction(
            "🗑️ " + _("apps_uninstall", "Uninstall"), self.main_window)
        act_uninstall.triggered.connect(lambda: self.uninstall_app(app))
        menu.addAction(act_uninstall)

        menu.exec_(QCursor.pos())

    def open_edit_dialog(self, app):
        """Opens the repair/edit dialog for the selected application."""
        from core.services.edit_app_dialog import AppEditDialog

        # Map keys to dialog expected format
        app_data_for_dialog = {
            "id": app["id"],
            "name": app["name"],
            "current_version": app["ver"],
            "local_path": app["dir"],
            "exe_path": app["exe"]
        }

        dialog = AppEditDialog(app_data_for_dialog, self.db, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
            if hasattr(self.main_window, 'dashboard_controller'):
                self.main_window.dashboard_controller.refresh_dashboard()

    def toggle_app_favorite(self, app_id, current_status, app_name="Unknown"):
        """Toggles the favorite status in the database and refreshes UI."""
        new_status = 1 if current_status == 0 else 0

        try:
            if hasattr(self.db, 'toggle_favorite'):
                self.db.toggle_favorite(app_id, new_status)
                self.refresh_data()
                log_key = "act_fav_added" if new_status == 1 else "act_fav_removed"
                self.log_app_activity(log_key, "launch", app_name)
            else:
                logger.error(
                    "Method 'toggle_favorite' was not found on the database object.")
        except Exception as e:
            logger.error(f"Failed to toggle favorite status: {e}")

    def log_app_activity(self, log_key, event_type, app_name):
        """Helper function for centralized activity logging."""
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                log_key,
                event_type=event_type,
                params={"app_name": app_name}
            )
