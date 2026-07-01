import os
import shutil
import subprocess
import webbrowser

from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileIconProvider,
                             QGridLayout, QMenu, QMessageBox)

from core.utils import get_folder_size_gb, is_update_available
from locales.localization import _
from locales.ui_localizer import localize_myapps_page
from ui.dialogs.dialog_utils import create_styled_msgbox, ask_confirmation
from ui.widgets.app_library_card import AppLibraryCard

"""
This file manages the "My Apps" page, displaying the list of installed applications, 
filtering, and providing management options.
"""


class MyAppsController:
    """Central controller for the 'My Apps' library page."""

    def __init__(self, main_window, ui, db):
        self.main_window = main_window
        self.ui = ui
        self.db = db
        self.view_mode = "grid"

        self.cached_apps = []
        self.icon_cache = {}
        self.icon_provider = QFileIconProvider()

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
            if db_exe_path and os.path.exists(db_exe_path):
                target_dir = os.path.dirname(db_exe_path)
            else:
                return None
        if not os.path.isabs(target_dir) and hasattr(self.main_window, 'portable_root'):
            target_dir = os.path.join(
                self.main_window.portable_root, target_dir)
        target_dir = os.path.normpath(target_dir)
        if hasattr(self.main_window, 'portable_root'):
            root_norm = os.path.normpath(self.main_window.portable_root)
            if target_dir == root_norm:
                return None
        return target_dir

    def refresh_data(self):
        """Loads all application data from the database into memory."""
        try:
            apps = self.db.get_all_apps()
        except AttributeError:
            return

        self.cached_apps = []

        # Get current installation root from settings
        current_root = ""
        if self.portable_root:
            current_root = os.path.normpath(self.portable_root)

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
            size_gb = get_folder_size_gb(safe_dir)

            # Check for version updates
            latest_ver = db_latest_ver  # Αν η βάση έχει NULL, αυτό θα γίνει None
            has_update = is_update_available(ver, latest_ver)

            if db_exe and os.path.exists(db_exe) and db_exe not in self.icon_cache:
                self.icon_cache[db_exe] = self.icon_provider.icon(
                    QFileInfo(db_exe)).pixmap(48, 48)

            self.cached_apps.append({
                "id": app_id, "name": name, "dir": safe_dir, "exe": db_exe,
                "ver": ver, "has_update": has_update, "latest_ver": latest_ver,
                "size_gb": size_gb, "source": source, "update_url": update_url,
                "homepage": homepage, "is_favorite": is_favorite
            })

        self.render_apps()

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

        total_gb = sum(a["size_gb"] for a in self.cached_apps)
        updates_count = sum(1 for a in self.cached_apps if a["has_update"])

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

        if hasattr(self.ui, 'myApps_lblStats'):
            stats_text = (
                f"{len(self.cached_apps)} " + _("apps_installed", "Applications Installed") +
                f" | {total_gb:.2f} GB | {updates_count} " +
                _("apps_updates_avail", "Updates Available")
            )
            self.ui.myApps_lblStats.setText(stats_text)

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
            except Exception as e:
                print(f"Error: {e}")
                self.log_app_activity("act_launch_failed", "error", app_name)

    def uninstall_app(self, app):
        if ask_confirmation(
            self.main_window,
            'Επιβεβαίωση Κατάργησης',
            f"Είστε σίγουροι ότι θέλετε να απεγκαταστήσετε πλήρως το {app['name']};\nΌλα τα δεδομένα της εφαρμογής θα διαγραφούν μόνιμα."
        ):
            try:
                target_dir = app["dir"]
                if not target_dir or target_dir == getattr(self.main_window, 'portable_root', ''):
                    create_styled_msgbox(
                        self.main_window, "Σφάλμα Ασφαλείας", "Ακύρωση: Ο φάκελος της εφαρμογής δεν βρέθηκε με ασφάλεια.").exec_()
                    return
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                if hasattr(self.db, 'delete_app'):
                    self.db.delete_app(app["name"])
                self.refresh_data()
                if hasattr(self.main_window, 'activity_manager'):
                    self.log_app_activity(
                        "act_uninstalled_app", "error", app.get('name'))

                create_styled_msgbox(
                    self.main_window, "Επιτυχία", f"Η εφαρμογή {app['name']} καταργήθηκε επιτυχώς!").exec_()
            except Exception as e:
                create_styled_msgbox(
                    self.main_window, "Σφάλμα", f"Αποτυχία κατάργησης: {e}").exec_()

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
        act_folder.triggered.connect(lambda _, d=app_folder: os.startfile(d) if d and os.path.exists(
            d) else QMessageBox.critical(self.main_window, "Σφάλμα", f"Ο φάκελος δεν βρέθηκε ή δεν είναι έγκυρος:\n{d}"))
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
                print(
                    "[ERROR] Η μέθοδος 'toggle_favorite' δεν βρέθηκε στο αντικείμενο database.")
        except Exception as e:
            print(f"[ERROR] Αποτυχία αλλαγής Favorite κατάστασης: {e}")

    def log_app_activity(self, log_key, event_type, app_name):
        """Helper function for centralized activity logging."""
        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                log_key,
                event_type=event_type,
                params={"app_name": app_name}
            )
