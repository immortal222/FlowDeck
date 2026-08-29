# Standard Library Imports
import os

# Third-Party Library Imports
from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

# Local Module Imports
from core.services.path_manager import PathManager
from core.utils import is_update_available
from locales.localization import _


class FavoriteCard(QFrame):
    """Widget representing a favorite application card on the Dashboard."""

    def __init__(self, app_data, icon_provider, portable_root, launch_callback, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.launch_callback = launch_callback

        name = app_data.get('name', 'Unknown')
        db_folder = app_data.get('local_path', '')
        db_exe = app_data.get('exe_path', '')
        ver = app_data.get('current_version', '1.0')
        lat = app_data.get('latest_version', ver)

        # Path setup
        self.safe_dir = PathManager.to_absolute_path(
            db_folder) if db_folder else ""

        # UI Setup
        self.setObjectName("appCard")
        self.setFixedSize(130, 110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Icon (Top)
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(30, 30)
        self.icon_lbl.setScaledContents(True)

        abs_db_exe = PathManager.to_absolute_path(db_exe) if db_exe else ""
        if abs_db_exe and os.path.exists(abs_db_exe):
            pixmap = icon_provider.icon(QFileInfo(abs_db_exe)).pixmap(30, 30)
            self.icon_lbl.setPixmap(pixmap)
        layout.addWidget(self.icon_lbl, alignment=Qt.AlignCenter)

        # Name (Below icon)
        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("appCard_Title")
        self.name_lbl.setWordWrap(True)

        # Dynamic font scaling based on text length
        metrics = self.name_lbl.fontMetrics()
        if metrics.width(name) > 100:  # Adjust based on actual width
            self.name_lbl.setStyleSheet("font-size: 10px;")
            self.name_lbl.setAlignment(Qt.AlignLeft)
        else:
            self.name_lbl.setStyleSheet("font-size: 12px;")
            self.name_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.name_lbl)

        # Version / Update
        self.ver_lbl = QLabel()
        self.ver_lbl.setObjectName("appCard_Version")
        self.ver_lbl.setAlignment(Qt.AlignCenter)

        if is_update_available(ver, lat):
            self.ver_lbl.setText(f"🚀 Update: {lat}")
            self.ver_lbl.setStyleSheet(
                "color: #F2A900; font-weight: bold; background: transparent; border: none;")
        else:
            self.ver_lbl.setText(f"v{ver}")
            self.ver_lbl.setStyleSheet(
                "color: #888888; background: transparent; border: none;")
        layout.addWidget(self.ver_lbl)

        layout.addStretch()

        # Launch Button
        self.btn_launch = QPushButton(_("dash_btn_launch", "Launch"))
        self.btn_launch.setObjectName("appCard_LaunchBtn")
        self.btn_launch.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_launch.clicked.connect(self._on_launch)
        layout.addWidget(self.btn_launch)

    def _on_launch(self):
        self.launch_callback(
            self.app_data.get('exe_path', ''),
            self.safe_dir,
            self.app_data.get('name', 'Unknown')
        )
