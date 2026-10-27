import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout)

from core.api.scoop_api import ScoopAPI
from core.catalog_service import CatalogService
from core.utils import find_app_executables
from locales.localization import _
from ui.styles.styles import DIALOG_LIGHT_STYLE, DIALOG_STYLE


class AppEditDialog(QDialog):
    """Dialog for editing application metadata and repairing broken paths."""

    def __init__(self, app_data, db, parent=None):
        super().__init__(parent)
        self.app_data = app_data  # Fields: id, name, current_version, local_path, exe_path
        self.db = db
        self.scoop_api = ScoopAPI()
        self.catalog = CatalogService()

        self.setWindowTitle(_("edit_dialog_title", "Edit & Repair"))
        self.setMinimumWidth(450)

        # Apply theme
        theme = "Modern Dark"
        if parent and hasattr(parent, 'settings_controller'):
            theme = parent.settings_controller.config.get(
                "theme", "Modern Dark")

        self.setStyleSheet(DIALOG_LIGHT_STYLE if theme ==
                           "Modern Light" else DIALOG_STYLE)

        self.init_ui()
        self.load_initial_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Application Name
        layout.addWidget(QLabel(_("edit_name_label", "Application Name:")))
        self.txt_name = QLineEdit()
        layout.addWidget(self.txt_name)

        # Version with Scoop validation
        layout.addWidget(QLabel(_("edit_version_label", "Version:")))
        h_ver_layout = QHBoxLayout()
        self.txt_version = QLineEdit()
        self.btn_scoop_val = QPushButton(
            _("edit_btn_validate", "🔍 Scoop Info"))
        self.btn_scoop_val.setToolTip(
            _("edit_tip_scoop", "Search Scoop catalog for metadata"))
        self.btn_scoop_val.clicked.connect(self.validate_with_scoop)
        h_ver_layout.addWidget(self.txt_version)
        h_ver_layout.addWidget(self.btn_scoop_val)
        layout.addLayout(h_ver_layout)

        # Executable with Smart Scan
        layout.addWidget(
            QLabel(_("edit_exe_label", "Executable File (.exe):")))
        h_exe_layout = QHBoxLayout()
        self.combo_exe = QComboBox()
        self.combo_exe.setEditable(True)
        self.btn_smart_scan = QPushButton(_("edit_btn_scan", "Smart Scan"))
        self.btn_smart_scan.clicked.connect(self.run_smart_scan)
        h_exe_layout.addWidget(self.combo_exe, 4)
        h_exe_layout.addWidget(self.btn_smart_scan, 1)
        layout.addLayout(h_exe_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton(_("edit_btn_save", "Save"))
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.clicked.connect(self.save_changes)

        self.btn_cancel = QPushButton(_("edit_btn_cancel", "Cancel"))
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_initial_data(self):
        """Populates fields with existing application data."""
        self.txt_name.setText(self.app_data.get('name', ''))
        self.txt_version.setText(self.app_data.get('current_version', '1.0'))

        exe_path = self.app_data.get('exe_path', '')
        local_path = self.app_data.get('local_path', '')

        self._initial_exe_path_full = exe_path
        self.combo_exe.setEditText(os.path.basename(exe_path))

        # Auto-trigger smart scan if executable is missing
        if local_path and exe_path:
            full_path = os.path.join(local_path, exe_path)
            if not os.path.exists(full_path):
                self.run_smart_scan()
                self.setWindowTitle(
                    _("edit_dialog_repair_mode", "Repair Application"))

    def validate_with_scoop(self):
        """Performs metadata lookup: Online -> Offline Mapping -> Online Re-query."""
        name = self.txt_name.text().strip()

        metadata = self.scoop_api.search_app(name)

        if not metadata or metadata == "SERVER_ERROR":
            mapped_id = self.catalog.get_scoop_id_by_name(name)
            if mapped_id:
                metadata = self.scoop_api.search_app(mapped_id)

        if metadata and isinstance(metadata, dict):
            found_version = metadata.get('version')
            current_version = self.txt_version.text().strip()

            if found_version and found_version != current_version:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle(_("edit_msg_title_confirm", "Confirmation"))
                msg.setText(_("edit_msg_found_version", "Version {version} found. Do you want to apply it?").format(
                    version=found_version))
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setStyleSheet(self.styleSheet())
                if msg.exec_() == QMessageBox.Yes:
                    self.txt_version.setText(found_version)
            self.btn_scoop_val.setText("✅ Found")
        else:
            self.btn_scoop_val.setText("❌ Not Found")

    def run_smart_scan(self):
        """Scans the application directory for executables and updates the selection list."""
        local_path = self.app_data.get('local_path')
        if not local_path or not os.path.exists(local_path):
            return

        exes = find_app_executables(local_path)
        self.combo_exe.clear()
        self.combo_exe.addItems(exes)
        if exes:
            self.combo_exe.setCurrentIndex(0)

    def save_changes(self):
        """Validates and persists changes to the database."""
        new_name = self.txt_name.text().strip()
        new_version = self.txt_version.text().strip()
        new_exe_display_text = self.combo_exe.currentText().strip()

        # Determine final executable path
        if new_exe_display_text == os.path.basename(self._initial_exe_path_full):
            new_exe = self._initial_exe_path_full
        else:
            # Construct full absolute path if a new relative executable path was chosen
            local_path = self.app_data.get('local_path', '')
            if local_path and not os.path.isabs(new_exe_display_text):
                new_exe = os.path.normpath(os.path.join(
                    local_path, new_exe_display_text)).replace("\\", "/")
            else:
                new_exe = new_exe_display_text.replace("\\", "/")

        if not new_name or not new_exe:
            return

        # Ensure name uniqueness if changed
        old_name = self.app_data.get('name', '')
        if new_name.lower() != old_name.lower():
            if self.db.get_app_by_name(new_name):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(_("edit_msg_title_error", "Error"))
                msg.setText(_("edit_msg_duplicate_name",
                            "The name '{name}' is already in use by another application.").format(name=new_name))
                msg.setStyleSheet(self.styleSheet())
                msg.exec_()
                return

        success = self.db.update_app_details(
            self.app_data['id'], new_name, new_version, new_exe)
        if success:
            self.accept()
