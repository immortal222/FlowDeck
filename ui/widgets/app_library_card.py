import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton)

from locales.localization import _
from core.services.path_manager import PathManager


class AppLibraryCard(QFrame):
    """Widget representing an application entry in the library view."""

    def __init__(self, app, view_mode, icon_pixmap, launch_callback, options_callback, is_favorite, parent=None):
        super().__init__(parent)
        self.app = app
        self.view_mode = view_mode
        self.icon_pixmap = icon_pixmap
        self.launch_callback = launch_callback
        self.options_callback = options_callback
        self.is_favorite = is_favorite

        # Preload favorite star pixmap using centralized PathManager
        self.star_pixmap = None
        try:
            star_path = PathManager.get_asset_path(
                os.path.join('icons', 'star.png'))
            if os.path.exists(star_path):
                self.star_pixmap = QPixmap(star_path)
        except Exception:
            self.star_pixmap = None

        self.setProperty("class", "AppCard")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda pos: self.options_callback(self.app))

        if self.view_mode == "grid":
            self.setup_grid_ui()
        else:
            self.setup_list_ui()

    def setup_grid_ui(self):
        """Configures the UI for grid view mode."""
        # Increase height to allow for two-line titles
        self.setFixedSize(200, 160)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(6)

        name_lbl = QLabel(self.app["name"])
        name_lbl.setProperty("class", "AppNameLabel")
        name_lbl.setWordWrap(True)

        # Dynamic font scaling based on title length
        metrics = name_lbl.fontMetrics()
        if metrics.width(self.app["name"]) > 150:
            name_lbl.setStyleSheet("font-size: 10px;")
            name_lbl.setAlignment(Qt.AlignLeft)
        else:
            name_lbl.setStyleSheet("font-size: 15px;")
            name_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(name_lbl)

        # Column distribution: Spacer | Icon | Version
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Left spacer / favorite star
        if self.is_favorite:
            star_lbl = QLabel()
            star_lbl.setProperty("class", "FavoriteStar")
            star_lbl.setFixedSize(16, 16)
            star_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            if self.star_pixmap and not self.star_pixmap.isNull():
                star_lbl.setPixmap(self.star_pixmap.scaled(
                    14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                star_lbl.setText("★")
            info_layout.addWidget(star_lbl)
            info_layout.addSpacing(4)
        else:
            placeholder = QLabel()
            placeholder.setFixedSize(16, 16)
            info_layout.addWidget(placeholder)
            info_layout.addSpacing(4)

        info_layout.addStretch(1)

        # Column 2: Centered icon
        icon_label = QLabel()
        icon_label.setFixedSize(42, 42)
        icon_label.setScaledContents(True)
        if self.icon_pixmap:
            icon_label.setPixmap(self.icon_pixmap)

        info_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        info_layout.addStretch(1)

        ver_lbl = QLabel(f"v{self.app['ver']}")
        ver_lbl.setProperty("class", "AppVersionLabel")
        ver_lbl.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        # Column 3: Version info
        info_layout.addWidget(ver_lbl, 1)

        layout.addLayout(info_layout)

        badge_lbl = QLabel()
        badge_text, badge_class = self.get_badge_info()
        badge_lbl.setText(badge_text)
        badge_lbl.setProperty("class", badge_class)
        badge_lbl.setAlignment(Qt.AlignCenter)
        badge_lbl.setFixedHeight(22)
        layout.addWidget(badge_lbl)

        btn_layout = QHBoxLayout()
        launch_btn = QPushButton(_("apps_btn_launch", "Launch"))
        launch_btn.setProperty("class", "AppLaunchButton")
        launch_btn.setCursor(Qt.PointingHandCursor)
        launch_btn.clicked.connect(lambda: self.launch_callback(
            self.app["exe"], self.app["name"]))

        options_btn = QPushButton("...")
        options_btn.setProperty("class", "AppOptionsButton")
        options_btn.setFixedSize(34, 34)
        options_btn.setCursor(Qt.PointingHandCursor)
        options_btn.clicked.connect(lambda: self.options_callback(self.app))

        btn_layout.addWidget(launch_btn)
        btn_layout.addWidget(options_btn)
        layout.addLayout(btn_layout)

    def setup_list_ui(self):
        """Configures the UI for list view mode."""
        self.setFixedHeight(75)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        # Favorite star (left of icon) for list view
        if self.is_favorite:
            list_star = QLabel()
            list_star.setProperty("class", "FavoriteStar")
            list_star.setFixedSize(16, 16)
            list_star.setAlignment(Qt.AlignCenter)
            if self.star_pixmap and not self.star_pixmap.isNull():
                list_star.setPixmap(self.star_pixmap.scaled(
                    14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                list_star.setText("★")
            layout.addWidget(list_star)
        else:
            spacer = QLabel()
            spacer.setFixedWidth(16)
            layout.addWidget(spacer)

        icon_label = QLabel()
        icon_label.setFixedSize(38, 38)
        icon_label.setScaledContents(True)
        if self.icon_pixmap:
            icon_label.setPixmap(self.icon_pixmap)
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        name_lbl = QLabel(self.app["name"])
        name_lbl.setProperty("class", "AppNameLabel")
        ver_lbl = QLabel(f"v{self.app['ver']}")
        ver_lbl.setProperty("class", "AppVersionLabel")
        text_layout.addWidget(name_lbl)
        text_layout.addWidget(ver_lbl)
        layout.addLayout(text_layout)

        layout.addStretch()

        badge_lbl = QLabel()
        badge_text, badge_class = self.get_badge_info()
        badge_lbl.setText(badge_text)
        badge_lbl.setProperty("class", badge_class)
        badge_lbl.setAlignment(Qt.AlignCenter)
        badge_lbl.setFixedSize(130, 26)
        layout.addWidget(badge_lbl)

        launch_btn = QPushButton(_("apps_btn_launch", "Launch"))
        launch_btn.setProperty("class", "AppLaunchButton")
        launch_btn.setFixedSize(90, 32)
        launch_btn.setCursor(Qt.PointingHandCursor)
        launch_btn.clicked.connect(lambda: self.launch_callback(
            self.app["exe"], self.app["name"]))
        layout.addWidget(launch_btn)

        options_btn = QPushButton("...")
        options_btn.setProperty("class", "AppOptionsButton")
        options_btn.setFixedSize(32, 32)
        options_btn.setCursor(Qt.PointingHandCursor)
        options_btn.clicked.connect(lambda: self.options_callback(self.app))
        layout.addWidget(options_btn)

    def get_badge_info(self):
        """Determines badge text and styling based on update status."""
        if self.app["has_update"]:
            return _("apps_update_to", "Update to v{ver}").format(ver=self.app['latest_ver']), "BadgeUpdate"
        elif not self.app["latest_ver"] or str(self.app["latest_ver"]).strip() in ["Unknown", "Portable", "None", "null", ""]:
            return _("apps_manual", "Manual"), "BadgeManual"
        else:
            return _("apps_latest", "Latest Version"), "BadgeLatest"
