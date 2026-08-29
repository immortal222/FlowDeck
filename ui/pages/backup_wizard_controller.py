# Standard Library Imports
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile

# Third-Party Library Imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QMessageBox

# Local Module Imports
from core.services.backup_manager import BackupManager
from core.services.path_manager import PathManager
from locales.localization import _
from locales.ui_localizer import localize_backup_wizard
from ui.generated.ui_backup_wizard import Ui_BackupWizardDialog
from ui.styles.style_export import (EXPORT_DARK_WIZARD_STYLE,
                                    EXPORT_LIGHT_WIZARD_STYLE)
from ui.styles.styles import DIALOG_LIGHT_STYLE, DIALOG_STYLE

logger = logging.getLogger(__name__)


class BackupWizardController:
    """Controller for managing the Backup and Restore wizard UI logic."""

    def __init__(self, main_window, db_manager):
        self.main_window = main_window
        self.db = db_manager
        self.config_manager = getattr(main_window, 'config_manager', None)
        self.backup_manager = BackupManager(self.db, self.config_manager)

    def open_wizard(self):
        """Initializes and displays the Backup/Restore wizard dialog."""
        wizard_dialog = QDialog(self.main_window)

        # Apply theme-specific styling
        current_theme = self.main_window.settings_controller.config.get(
            "theme", "Modern Dark")
        if current_theme == "Modern Light":
            wizard_dialog.setStyleSheet(EXPORT_LIGHT_WIZARD_STYLE)
            self.dialog_style = DIALOG_LIGHT_STYLE
        else:
            wizard_dialog.setStyleSheet(EXPORT_DARK_WIZARD_STYLE)
            self.dialog_style = DIALOG_STYLE

        ui_wizard = Ui_BackupWizardDialog()
        ui_wizard.setupUi(wizard_dialog)

        wizard_dialog.ui = ui_wizard
        localize_backup_wizard(wizard_dialog)

        # Auto-populate import destination from settings
        current_install_path = self.main_window.ui.txt_installPath.text().strip()
        ui_wizard.txt_importDestinationPath.setText(current_install_path)
        if not current_install_path:
            current_install_path = os.path.expanduser(
                "~/FlowDeck/Apps").replace("\\", "/")
            ui_wizard.txt_importDestinationPath.setText(current_install_path)

        ui_wizard.tabs_Backup.setCurrentIndex(0)

        if hasattr(ui_wizard, 'btn_closeWizard'):
            ui_wizard.btn_closeWizard.clicked.connect(wizard_dialog.reject)

        # UI Helper Functions
        def get_free_space(path):
            """Returns available disk space in bytes for the specified path."""
            check_path = path
            while check_path and not os.path.exists(check_path):
                check_path = os.path.dirname(check_path)
            if not check_path:
                check_path = "C:\\"
            return shutil.disk_usage(check_path).free

        def update_export_summary():
            """Updates export summary labels dynamically based on user selection."""
            checked_count = 0
            total_bytes = 0
            total_count = ui_wizard.list_fdaApps.count()

            for i in range(total_count):
                item = ui_wizard.list_fdaApps.item(i)
                if item.checkState() == Qt.Checked:
                    checked_count += 1
                    app_data = wizard_dialog.apps_data_map.get(item.text())
                    if app_data:
                        total_bytes += self.backup_manager.get_folder_size(
                            app_data.get("local_path", ""))

            lbl_size = getattr(ui_wizard, 'lblwIZ_SummarySize', getattr(
                ui_wizard, 'lblWiz_SummarySize', None))
            if lbl_size:
                size_mb = total_bytes / (1024 * 1024)
                lbl_size.setText(
                    _("bak_ctrl_total_size", "Συνολικό Μέγεθος (Ασυμπίεστο): {size} MB").format(size=f"{size_mb:.1f}"))

        def update_import_summary():
            """Updates import summary labels and validates disk space requirements."""
            checked_count = 0
            total_bytes = 0
            overwrite_count = 0
            total_count = ui_wizard.list_importApps.count()

            dest_path = ui_wizard.txt_importDestinationPath.text().strip()
            free_bytes = get_free_space(dest_path)

            for i in range(total_count):
                item = ui_wizard.list_importApps.item(i)
                if item.checkState() == Qt.Checked:
                    checked_count += 1
                    full_text = item.text()

                    app_name = full_text.strip().split(" (")[0].strip()

                    if _("bak_ctrl_overwrite_term", "Αντικατάσταση") in full_text:
                        overwrite_count += 1

                    if hasattr(wizard_dialog, 'import_apps_map') and app_name in wizard_dialog.import_apps_map:
                        total_bytes += wizard_dialog.import_apps_map[app_name].get(
                            "size_bytes", 0)

            if hasattr(ui_wizard, 'lblWiz_SummaryApps'):
                ui_wizard.lblWiz_SummaryApps.setText(
                    _("bak_ctrl_import_selected", "Επιλεγμένες Εφαρμογές: {checked} από {total}").format(
                        checked=checked_count, total=total_count))

            lbl_size = getattr(ui_wizard, 'lblwIZ_SummarySize', getattr(
                ui_wizard, 'lblWiz_SummarySize', None))
            if lbl_size:
                req_mb = total_bytes / (1024 * 1024)
                free_gb = free_bytes / (1024 * 1024 * 1024)
                lbl_size.setText(
                    _("bak_ctrl_space_req", "Απαιτούμενος Χώρος: {req} MB / Διαθέσιμος Χώρος: {free} GB").format(
                        req=f"{req_mb:.1f}", free=f"{free_gb:.1f}"))

                # Space availability validation
                if total_bytes > free_bytes and checked_count > 0:
                    lbl_size.setStyleSheet(
                        "color: #ff4444; font-weight: bold;")
                    if hasattr(ui_wizard, 'btn_startImport'):
                        ui_wizard.btn_startImport.setEnabled(False)
                else:
                    lbl_size.setStyleSheet("")
                    if hasattr(ui_wizard, 'btn_startImport') and checked_count > 0:
                        ui_wizard.btn_startImport.setEnabled(True)
                    elif hasattr(ui_wizard, 'btn_startImport') and checked_count == 0:
                        ui_wizard.btn_startImport.setEnabled(
                            False)

            if hasattr(ui_wizard, 'lblWiz_CurrentAction'):
                if checked_count == 0:
                    ui_wizard.lblWiz_CurrentAction.setText(
                        _("bak_ctrl_status_no_apps", "Κατάσταση: Καμία επιλεγμένη εφαρμογή"))
                    ui_wizard.lblWiz_CurrentAction.setStyleSheet("")
                elif overwrite_count > 0:
                    ui_wizard.lblWiz_CurrentAction.setText(
                        _("bak_ctrl_status_overwrite_warn", "Κατάσταση: ⚠️ {count} εφαρμογές θα αντικατασταθούν!").format(count=overwrite_count))
                    ui_wizard.lblWiz_CurrentAction.setStyleSheet(
                        "color: #ffaa00;")
                else:
                    ui_wizard.lblWiz_CurrentAction.setText(
                        _("bak_ctrl_status_new_apps", "Κατάσταση: Όλες οι επιλεγμένες εφαρμογές είναι νέες"))
                    ui_wizard.lblWiz_CurrentAction.setStyleSheet(
                        "color: #00aa00;")

        if hasattr(ui_wizard, 'lblWiz_FileName'):
            ui_wizard.txt_fdaPath.textChanged.connect(
                lambda text: ui_wizard.lblWiz_FileName.setText(_("bak_ctrl_filename", "Όνομα Αρχείου: {name}").format(name=os.path.basename(text))))
            ui_wizard.txt_importSourcePath.textChanged.connect(
                lambda text: ui_wizard.lblWiz_FileName.setText(_("bak_ctrl_filename", "Όνομα Αρχείου: {name}").format(name=os.path.basename(text))))

        # TAB 2: INITIALIZATION (EXPORT)
        if hasattr(ui_wizard, 'lblWiz_CurrentAction'):
            ui_wizard.lblWiz_CurrentAction.setText(
                _("bak_ctrl_status_ready_export", "Κατάσταση: Έτοιμο για εξαγωγή"))

        all_apps = self.db.get_all_apps()
        ui_wizard.list_fdaApps.clear()
        wizard_dialog.apps_data_map = {}

        ui_wizard.list_fdaApps.blockSignals(True)
        for app in all_apps:
            app_name = app.get("name", "Unknown")
            app_version = app.get("current_version", "1.0")
            size_bytes = self.backup_manager.get_folder_size(
                app.get("local_path", ""))
            size_mb = size_bytes / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{(size_mb/1024):.1f} GB"

            item_text = _("bak_ctrl_app_item_format", " {name} (v{version})  —  [{size}]").format(
                name=app_name, version=app_version, size=size_str)
            item = QListWidgetItem(item_text, ui_wizard.list_fdaApps)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            wizard_dialog.apps_data_map[item_text] = app
        ui_wizard.list_fdaApps.blockSignals(False)

        ui_wizard.list_fdaApps.itemChanged.connect(update_export_summary)
        if hasattr(ui_wizard, 'rad_ultra_7z'):
            ui_wizard.rad_ultra_7z.toggled.connect(update_export_summary)

        def handle_zip_browse():
            if hasattr(ui_wizard, 'rad_ultra_7z') and ui_wizard.rad_ultra_7z.isChecked():
                file_filter = _("bak_ctrl_filter_7z", "7-Zip Archive (*.7z)")
                default_filename = "flowdeck_export.7z"
                default_ext = ".7z"
            else:
                file_filter = _("bak_ctrl_filter_zip", "Zip Archive (*.zip)")
                default_filename = "flowdeck_export.zip"
                default_ext = ".zip"

            default_path = os.path.join(os.path.expanduser(
                "~/Desktop"), default_filename).replace("\\", "/")

            save_dialog = QFileDialog(wizard_dialog)
            if 'DIALOG_STYLE' in globals() or 'DIALOG_STYLE' in locals():
                save_dialog.setStyleSheet(DIALOG_STYLE)

            file_path, selected_filter = save_dialog.getSaveFileName(
                wizard_dialog, _("bak_ctrl_save_title", "Αποθήκευση Αρχείου Μεταφοράς"), default_path, file_filter)
            if file_path:
                if not file_path.lower().endswith(default_ext):
                    file_path += default_ext
                ui_wizard.txt_fdaPath.setText(file_path)

        if hasattr(ui_wizard, 'btn_fdaBrowse'):
            try:
                ui_wizard.btn_fdaBrowse.clicked.disconnect()
            except:
                pass
            ui_wizard.btn_fdaBrowse.clicked.connect(handle_zip_browse)

        if hasattr(ui_wizard, 'progress_fda'):
            ui_wizard.progress_fda.setValue(0)
            ui_wizard.progress_fda.setVisible(False)

        def handle_zip_export():
            target_path = ui_wizard.txt_fdaPath.text().strip()
            if not target_path:
                msg = QMessageBox(wizard_dialog)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("set_msg_title_error", "Σφάλμα"))
                msg.setText(
                    _("bak_ctrl_err_dest", "Παρακαλώ επιλέξτε διαδρομή αποθήκευσης!"))
                msg.setStyleSheet(self.dialog_style)

                msg.exec_()
                return

            selected_apps_to_export = [wizard_dialog.apps_data_map[ui_wizard.list_fdaApps.item(i).text()]
                                       for i in range(ui_wizard.list_fdaApps.count())
                                       if ui_wizard.list_fdaApps.item(i).checkState() == Qt.Checked]

            if not selected_apps_to_export:
                msg = QMessageBox(wizard_dialog)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("set_msg_title_error", "Σφάλμα"))
                msg.setText(_("bak_ctrl_err_no_select",
                            "Δεν έχετε επιλέξει καμία εφαρμογή!"))
                msg.setStyleSheet(self.dialog_style)
                msg.exec_()
                return

            if hasattr(ui_wizard, 'rad_ultra_7z') and ui_wizard.rad_ultra_7z.isChecked():
                correct_ext = ".7z"
            else:
                correct_ext = ".zip"

            if target_path.lower().endswith(".zip") or target_path.lower().endswith(".7z"):
                target_path = target_path.rsplit(".", 1)[0]
            target_path += correct_ext
            ui_wizard.txt_fdaPath.setText(target_path)

            ui_wizard.btn_createFdaArchive.setEnabled(False)
            ui_wizard.progress_fda.setVisible(True)

            self.backup_manager.progress_changed.connect(
                ui_wizard.progress_fda.setValue)

            # Σύνδεση του Live Status Label
            if hasattr(ui_wizard, 'lbl_fdaCurrentAppProcessing'):
                self.backup_manager.status_changed.connect(
                    ui_wizard.lbl_fdaCurrentAppProcessing.setText)

            if hasattr(ui_wizard, 'lblWiz_CurrentAction'):
                self.backup_manager.status_changed.connect(
                    ui_wizard.lblWiz_CurrentAction.setText)

            def on_export_finished(success, message):
                try:
                    self.backup_manager.finished.disconnect()
                    self.backup_manager.status_changed.disconnect()
                except:
                    pass

                if hasattr(ui_wizard, 'lbl_fdaCurrentAppProcessing'):
                    ui_wizard.lbl_fdaCurrentAppProcessing.setText("")

                msg = QMessageBox(wizard_dialog)
                if success:
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle(_("set_msg_title_success", "Επιτυχία"))
                else:
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle(_("set_msg_title_error", "Σφάλμα"))
                msg.setText(message)
                msg.setStyleSheet(self.dialog_style)
                msg.exec_()
                if success:
                    wizard_dialog.accept()

            self.backup_manager.finished.connect(on_export_finished)

            self.backup_manager.export_to_zip(
                selected_apps_to_export, target_path)

        if hasattr(ui_wizard, 'btn_createFdaArchive'):
            ui_wizard.btn_createFdaArchive.clicked.connect(handle_zip_export)

        # TAB 3: INITIALIZATION (IMPORT / RESTORE)
        wizard_dialog.import_apps_map = {}

        def handle_import_source_browse():
            file_path, selected_filter = QFileDialog.getOpenFileName(
                wizard_dialog, _("bak_ctrl_import_title",
                                 "Επιλέξτε Αρχείο Μεταφοράς"),
                os.path.expanduser(
                    "~/Desktop"), _("bak_ctrl_import_filter", "Archives (*.7z *.zip)")
            )
            if not file_path:
                return

            ui_wizard.txt_importSourcePath.setText(file_path)
            ui_wizard.list_importApps.blockSignals(True)
            ui_wizard.list_importApps.clear()
            wizard_dialog.import_apps_map.clear()

            try:
                seven_zip_path = PathManager.get_bin_path("7za.exe")
                with tempfile.TemporaryDirectory() as t_dir:
                    cmd = [seven_zip_path, "e", file_path,
                           "manifest.json", f"-o{t_dir}", "-y"]
                    startupinfo = None
                    if sys.platform == "win32":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    p = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                    p.communicate()

                    m_path = os.path.join(t_dir, "manifest.json")
                    if not os.path.exists(m_path):
                        raise Exception(
                            _("bak_ctrl_invalid_backup", "Το αρχείο δεν είναι έγκυρο backup (λείπει το manifest.json)."))

                    with open(m_path, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)

                dest_path = ui_wizard.txt_importDestinationPath.text().strip()
                abs_dest_path = PathManager.to_absolute_path(
                    dest_path) if dest_path else ""

                def compare_versions(v1, v2):
                    try:
                        p1 = [int(x)
                              for x in str(v1).split('.') if x.isdigit()]
                        p2 = [int(x)
                              for x in str(v2).split('.') if x.isdigit()]
                        length = max(len(p1), len(p2))
                        p1 += [0] * (length - len(p1))
                        p2 += [0] * (length - len(p2))
                        if p1 > p2:
                            return 1
                        elif p1 < p2:
                            return -1
                        return 0
                    except:
                        if str(v1) > str(v2):
                            return 1
                        elif str(v1) < str(v2):
                            return -1
                        return 0

                for app in manifest_data.get("apps", []):
                    app_name = app.get("name")
                    folder_name = app.get("local_path")
                    import_version = app.get("current_version", "1.0")

                    wizard_dialog.import_apps_map[app_name] = app

                    db_app = self.main_window.db.get_app_by_name(app_name)
                    exists_in_db = db_app is not None
                    target_folder = os.path.join(
                        abs_dest_path, folder_name) if abs_dest_path and folder_name else ""
                    exists_on_disk = os.path.exists(
                        target_folder) if target_folder else False

                    if exists_in_db:
                        db_version = db_app.get("current_version", "1.0")
                        cmp_res = compare_versions(import_version, db_version)
                        if cmp_res > 0:
                            ver_text = _("bak_ctrl_ver_prev", "προηγούμενη")
                        elif cmp_res < 0:
                            ver_text = _("bak_ctrl_ver_next", "νεότερη")
                        else:
                            ver_text = _("bak_ctrl_ver_same", "ίδια")
                        display_text = _("bak_ctrl_app_exists", "{name} (Υπάρχει ήδη σε {ver} έκδοση - Αντικατάσταση;)").format(
                            name=app_name, ver=ver_text)
                        check_state = Qt.Unchecked
                    elif exists_on_disk:
                        display_text = _(
                            "bak_ctrl_folder_exists", "{name} (Ο φάκελος υπάρχει ήδη - Αντικατάσταση;)").format(name=app_name)
                        check_state = Qt.Unchecked
                    else:
                        display_text = _(
                            "bak_ctrl_app_new", "{name} (Νέα - v{ver})").format(name=app_name, ver=import_version)
                        check_state = Qt.Checked

                    item = QListWidgetItem(display_text)
                    item.setCheckState(check_state)
                    ui_wizard.list_importApps.addItem(item)

            except Exception as e:
                logger.error(f"Error reading file during browse: {e}")
            finally:
                ui_wizard.list_importApps.blockSignals(False)
                update_import_summary()

        if hasattr(ui_wizard, 'btn_importSourceBrowse'):
            ui_wizard.btn_importSourceBrowse.clicked.connect(
                handle_import_source_browse)

        ui_wizard.list_importApps.itemChanged.connect(update_import_summary)

        def handle_import_dest_browse():
            folder_path = QFileDialog.getExistingDirectory(
                wizard_dialog, _("bak_ctrl_dest_title", "Επιλέξτε Φάκελο Εγκατάστασης Εφαρμογών"), "C:\\")
            if folder_path:
                ui_wizard.txt_importDestinationPath.setText(folder_path)
                update_import_summary()

        if hasattr(ui_wizard, 'btn_importDestinationBrowse'):
            ui_wizard.btn_importDestinationBrowse.clicked.connect(
                handle_import_dest_browse)

        if hasattr(ui_wizard, 'progress_import'):
            ui_wizard.progress_import.setValue(0)
            ui_wizard.progress_import.setVisible(False)

        def handle_start_import():
            source_path = ui_wizard.txt_importSourcePath.text().strip()
            raw_dest_path = ui_wizard.txt_importDestinationPath.text().strip()

            if not raw_dest_path:
                raw_dest_path = os.path.expanduser(
                    "~/FlowDeck/Apps").replace("\\", "/")

            dest_path = PathManager.to_absolute_path(raw_dest_path)

            if not source_path:
                msg = QMessageBox(wizard_dialog)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("set_msg_title_error", "Σφάλμα"))
                msg.setText(
                    _("bak_ctrl_err_source", "Παρακαλώ επιλέξτε το αρχείο εισαγωγής (.7z ή .zip)!"))
                msg.setStyleSheet(self.dialog_style)
                msg.exec_()
                return

            ui_wizard.btn_startImport.setEnabled(False)
            ui_wizard.progress_import.setVisible(True)

            self.backup_manager.progress_changed.connect(
                ui_wizard.progress_import.setValue)

            if hasattr(ui_wizard, 'lblWiz_ImmportAppLive'):
                self.backup_manager.status_changed.connect(
                    ui_wizard.lblWiz_ImmportAppLive.setText)

            def on_import_finished(success, message):
                ui_wizard.btn_startImport.setEnabled(True)
                try:
                    self.backup_manager.finished.disconnect()
                    self.backup_manager.progress_changed.disconnect()
                    if hasattr(ui_wizard, 'lblWiz_ImmportAppLive'):
                        self.backup_manager.status_changed.disconnect()
                except:
                    pass

                msg = QMessageBox(wizard_dialog)
                if success:
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle(_("set_msg_title_success", "Επιτυχία"))
                else:
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle(_("set_msg_title_error", "Σφάλμα"))
                msg.setText(message)
                msg.setStyleSheet(self.dialog_style)
                msg.exec_()

                if success:
                    if hasattr(self.main_window, 'my_apps_page_controller') and hasattr(self.main_window.my_apps_page_controller, 'load_apps'):
                        self.main_window.my_apps_page_controller.load_apps()
                    if hasattr(self.main_window, 'dashboard_controller') and hasattr(self.main_window.dashboard_controller, 'load_favorites'):
                        self.main_window.dashboard_controller.load_favorites()
                    wizard_dialog.accept()

            self.backup_manager.finished.connect(on_import_finished)

            selected_apps = []
            for i in range(ui_wizard.list_importApps.count()):
                item = ui_wizard.list_importApps.item(i)
                if item.checkState() == Qt.Checked:
                    app_name = item.text().split(" (")[0].strip()
                    selected_apps.append(app_name)

            import_settings = False
            if hasattr(ui_wizard, 'cbx_importSetting'):
                import_settings = ui_wizard.cbx_importSetting.isChecked()

            self.backup_manager.import_from_zip(
                source_path, dest_path, selected_apps, import_settings)

        def toggle_all_import_apps(is_checked):
            check_state = Qt.Checked if is_checked else Qt.Unchecked
            if hasattr(ui_wizard, 'list_importApps'):
                ui_wizard.list_importApps.blockSignals(True)
                for i in range(ui_wizard.list_importApps.count()):
                    item = ui_wizard.list_importApps.item(i)
                    if item:
                        item.setCheckState(check_state)
                ui_wizard.list_importApps.blockSignals(False)
                update_import_summary()

        if hasattr(ui_wizard, 'cbx_importAll'):
            try:
                ui_wizard.cbx_importAll.toggled.disconnect()
            except:
                pass
            ui_wizard.cbx_importAll.toggled.connect(toggle_all_import_apps)

        if hasattr(ui_wizard, 'btn_startImport'):
            try:
                ui_wizard.btn_startImport.clicked.disconnect()
            except:
                pass
            ui_wizard.btn_startImport.clicked.connect(handle_start_import)

        def toggle_all_export_apps(is_checked):
            check_state = Qt.Checked if is_checked else Qt.Unchecked
            if hasattr(ui_wizard, 'list_fdaApps'):
                ui_wizard.list_fdaApps.blockSignals(True)
                for i in range(ui_wizard.list_fdaApps.count()):
                    item = ui_wizard.list_fdaApps.item(i)
                    if item:
                        item.setCheckState(check_state)
                ui_wizard.list_fdaApps.blockSignals(False)
                update_export_summary()

        if hasattr(ui_wizard, 'cbx_fdaAll'):
            try:
                ui_wizard.cbx_fdaAll.toggled.disconnect()
            except:
                pass
            ui_wizard.cbx_fdaAll.toggled.connect(toggle_all_export_apps)

        update_export_summary()

        wizard_dialog.exec_()
