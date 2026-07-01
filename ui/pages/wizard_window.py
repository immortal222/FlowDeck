import hashlib
import os
import platform
import re
import shutil
import subprocess
import webbrowser
import zipfile
import pefile

import requests
import win32com.client
from PyQt5.QtCore import QEvent, QObject, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QHBoxLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QVBoxLayout, QComboBox)

from core.api.chocolatey_api import ChocolateyAPI
from core.api.scoop_api import ScoopAPI
from core.services.installer import AppInstaller
from core.services.path_manager import PathManager
from core.utils import get_portable_apps_metadata, is_internet_available, get_pe_version, get_pe_name
from locales.localization import _
from locales.ui_localizer import localize_wizard_page
from ui.styles.styles import DIALOG_STYLE, DIALOG_LIGHT_STYLE


class UnifiedInstallDialog(QDialog):
    """Single unified dialog for confirming App Name, Version, and Executable."""

    def __init__(self, app_name, version, exes, scoop_ver, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            _("wiz_confirm_title", "Confirm Installation Details"))
        self.setMinimumWidth(450)

        # Apply dynamic theme styling
        theme = "Modern Dark"
        if hasattr(parent, 'settings_controller') and parent.settings_controller:
            theme = parent.settings_controller.config.get(
                "theme", "Modern Dark")
        style = DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE
        self.setStyleSheet(style)

        layout = QVBoxLayout(self)

        # 1. App Name
        layout.addWidget(QLabel(_("wiz_step2_msg", "Application Name:")))
        self.name_input = QLineEdit(app_name)
        layout.addWidget(self.name_input)

        # 2. Version
        layout.addWidget(QLabel(_("wiz_step5_title", "Version:")))
        ver_layout = QHBoxLayout()
        self.ver_input = QLineEdit(version)
        ver_layout.addWidget(self.ver_input)

        if scoop_ver:
            self.btn_set_scoop = QPushButton(
                _("wiz_step5_set_scoop", f"← Use Scoop ({scoop_ver})"))
            self.btn_set_scoop.clicked.connect(
                lambda: self.ver_input.setText(scoop_ver))
            ver_layout.addWidget(self.btn_set_scoop)
        layout.addLayout(ver_layout)

        # 3. Executable Selection
        layout.addWidget(
            QLabel(_("wiz_title_select_exe", "Select Executable:")))
        self.exe_combo = QComboBox()
        self.exe_combo.addItems(exes)
        layout.addWidget(self.exe_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_next = QPushButton(_("wiz_next", "Install"))
        self.btn_next.setObjectName("primaryButton")
        self.btn_cancel = QPushButton(_("wiz_cancel", "Cancel"))

        self.btn_next.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.ver_input.text().strip(),
            self.exe_combo.currentText()
        )


class WizardController(QObject):
    """Controller managing the installation flow, API integrations, and UI state."""

    def __init__(self, main_window, ui, db):
        super().__init__(main_window)
        self.main_window = main_window
        self.ui = ui
        self.db = db

        # Localize static UI elements
        localize_wizard_page(self)

        # API Backend initialization
        self.scoop = ScoopAPI()
        self.choco = ChocolateyAPI()

        self.current_file_path = ""
        self.detected_version_regex = ""
        self.current_app_url = ""
        self._is_installing = False  # Safety lock for double clicks

        self.setup_ui_connections()

    def get_msg_style(self):
        """Returns dynamic style for Message Boxes based on theme."""
        theme = self.main_window.settings_controller.config.get(
            "theme", "Modern Dark")
        return DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE

    @property
    def portable_root(self):
        """Always reads the current installation path from settings."""
        return self.main_window.settings_controller.config.get("install_path")

    def setup_ui_connections(self):
        self.ui.categoryCombo.clear()
        self.ui.categoryCombo.addItems(
            ["Tools", "Internet", "Multimedia", "Games", "Other"])

        self.ui.browseButton.clicked.connect(self.browse_file)
        self.ui.installButton.clicked.connect(self.start_install_from_button)

        self.ui.DnDframe.setAcceptDrops(True)
        self.ui.DnDframe.installEventFilter(self)

        if hasattr(self.ui, 'sidebarUrlBtn'):
            self.ui.sidebarUrlBtn.clicked.connect(self.open_app_website)

        if hasattr(self.ui, 'consoleEdit'):
            self.ui.consoleEdit.clear()
            self.log(
                _("wiz_log_sys_ready", "System ready. Waiting for .zip or .7z file..."))

        # Initialize Store buttons
        apps_setup = {
            "popularBtn_Keepass": {"scoop_id": "keepass", "img": "keepass.png"},
            "popularBtn_Notepad": {"scoop_id": "notepadplusplus", "img": "notepadplusplus.png"},
            "popularBtn_XnViewMP": {"scoop_id": "xnviewmp", "img": "xnviewmp.png"},
            "popularBtn_Vlc": {"scoop_id": "vlc", "img": "vlc.png"},
            "popularBtn_7zip": {"scoop_id": "7zip", "img": "7zip.png"},
            "popularBtn_Brave": {"scoop_id": "brave", "img": "brave.png"}
        }

        assets_apps_path = PathManager.get_asset_path("apps")

        for btn_name, info in apps_setup.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)

                try:
                    btn.clicked.disconnect()
                except TypeError:
                    pass

                btn.clicked.connect(
                    lambda checked, s_id=info["scoop_id"]: self.start_quick_install(s_id))

                img_path = os.path.join(assets_apps_path, info["img"])
                if os.path.exists(img_path):
                    btn.setIcon(QIcon(img_path))
                    btn.setIconSize(QSize(24, 24))

                    css_path = img_path.replace('\\', '/')
                    btn.setStyleSheet(f"""
                        QPushButton, QToolButton {{
                            text-align: left;
                            padding-left: 50px; 
                        }}
                    """)

    def log(self, message):
        if hasattr(self.ui, 'consoleEdit'):
            self.ui.consoleEdit.append(f"> {message}")
        if hasattr(self.ui, 'statusLabel'):
            self.ui.statusLabel.setText(message)
        QApplication.processEvents()

    def smart_search_app(self, app_name):
        """Searches Scoop first; falls back to Chocolatey if not found or if only installer is available."""
        if not is_internet_available():
            self.log(_("upd_no_internet_text",
                     "Unable to connect to the internet."))
            return None

        app_data = self.scoop.search_app(app_name)

        if not isinstance(app_data, dict):
            app_data = None

        is_exe = False
        if app_data:
            url = app_data.get('url')

            if not url and app_data.get('architecture'):
                arch = app_data['architecture']
                if '64bit' in arch:
                    url = arch['64bit'].get('url')
                elif '32bit' in arch:
                    url = arch['32bit'].get('url')

            if url:
                if isinstance(url, list) and len(url) > 0:
                    url = url[0]
                clean_url = str(url).split('#/')[0].split('?')[0]
                if clean_url.lower().endswith('.exe') or clean_url.lower().endswith('.msi'):
                    is_exe = True

        if not app_data or is_exe:
            if is_exe:
                self.log(_("wiz_log_scoop_exe_warn",
                         "⚠️ Scoop returned an installer (.exe). Searching for portable version in Chocolatey..."))
            else:
                self.log(_("wiz_log_scoop_not_found",
                         "🔍 Not found in Scoop. Searching in Chocolatey..."))

            choco_data = self.choco.search_app(app_name)
            if choco_data:
                return choco_data

        if app_data:
            app_data["source"] = "scoop"

        return app_data

    def update_sidebar(self, app_name, scoop_data, local_version=""):
        """Updates the information sidebar with application metadata and version comparison."""
        if not hasattr(self.ui, 'sidebarTitle'):
            return

        self.ui.sidebarTitle.setText(
            _("wiz_app_info", "App Information"))
        icon = "📦"
        desc = _("wiz_no_desc", "No description available.")
        version_text = _("wiz_local", "Local Only")
        status_text = ""
        url_enabled = False
        self.current_app_url = ""
        icon_path = None

        if local_version == _("wiz_waiting", "Waiting..."):
            icon = "🔍"
            version_text = _("wiz_waiting", "Waiting...")
            status_text = f"<span style='color: #888888;'>{_('wiz_searching_api', 'Searching API...')}</span>"
            desc = _("wiz_analyzing_file",
                     "Analyzing file and searching for online metadata...")
        elif scoop_data:
            icon = "📦" if scoop_data.get('source') == 'scoop' else "🍫"

            scoop_version = scoop_data.get(
                'version', _("wiz_unknown", "Unknown"))
            desc = scoop_data.get('description', _(
                "wiz_no_desc", "No description available."))
            if not local_version:
                version_text = f"v{scoop_version} ({_('wiz_first_install', 'First installation')})"
                status_text = f"<span style='color: #4caf50;'>{_('wiz_new_installation', 'New Installation')}</span>"
            else:
                version_text = f"v{scoop_version} (Local: v{local_version})"
                if local_version == scoop_version:
                    status_text = f"<span style='color: #2196F3;'>{_('wiz_latest_version', 'Latest Version')}</span>"
                else:
                    status_text = f"<span style='color: #ff9800;'>{_('wiz_update_available', 'New Version Available')}</span>"

            homepage = scoop_data.get('homepage', '')
            if isinstance(homepage, list) and len(homepage) > 0:
                homepage = homepage[0]
            self.current_app_url = homepage
            url_enabled = bool(self.current_app_url)
        else:
            icon = "❓"
            version_text = f"v{local_version if local_version else '1.0'} (Local)"
            status_text = f"<span style='color: #ff4c4c;'>{_('wiz_out_of_api', 'Outside API')}</span>"
            desc = _("wiz_no_online_info",
                     "No online information found. Installation will proceed using local data.")

        # Handle icon or emoji rendering
        if hasattr(self.ui, 'sidebarIcon'):
            is_paf = hasattr(self, 'current_file_path') and (self.current_file_path.lower(
            ).endswith('.paf') or self.current_file_path.lower().endswith('.paf.exe'))

            icon_path = None
            if is_paf:
                try:
                    folders = [os.path.join(self.portable_root, d) for d in os.listdir(
                        self.portable_root) if os.path.isdir(os.path.join(self.portable_root, d))]
                    if folders:
                        latest_folder = max(folders, key=os.path.getmtime)
                        possible_ico = os.path.join(
                            latest_folder, "App", "AppInfo", "appicon.ico")
                        if os.path.exists(possible_ico):
                            icon_path = possible_ico
                except Exception:
                    pass

            if icon_path and os.path.exists(icon_path):
                pixmap = QIcon(icon_path).pixmap(50, 50)

                self.ui.sidebarIcon.clear()
                self.ui.sidebarIcon.setPixmap(pixmap)
                self.ui.sidebarIcon.setAlignment(Qt.AlignCenter)

            # Fallback to emoji
            else:
                self.ui.sidebarIcon.clear()
                self.ui.sidebarIcon.setText(icon)
                self.ui.sidebarIcon.setStyleSheet("font-size: 50px;")
                self.ui.sidebarIcon.setAlignment(Qt.AlignCenter)

        if hasattr(self.ui, 'sidebarUrlBtn'):
            self.ui.sidebarUrlBtn.setEnabled(url_enabled)
            self.ui.sidebarUrlBtn.setText(
                _("wiz_official_site", "🌐 Official Site") if url_enabled else _("wiz_no_site", "Not Available"))

        display_name = scoop_data.get(
            'name', app_name) if scoop_data else app_name
        if display_name.lower().replace(" ", "") == "notepadplusplus":
            display_name = "Notepad++"

        theme = "Modern Dark"
        if hasattr(self.main_window, 'settings_controller'):
            theme = self.main_window.settings_controller.config.get(
                "theme", "Modern Dark")

        if theme == "Modern Light":
            text_color = "#333333"
            hr_color = "#CCCCCC"
            desc_color = "#555555"
        else:
            text_color = "#DBE5EB"
            hr_color = "#474747"
            desc_color = "#AAAAAA"

        rich_text = f"""
        <div style='font-size: 13px; color: {text_color}; line-height: 1.5;'>
            <p><b>{_('wiz_side_app_name', 'App Name')}:</b> {display_name}</p>
            <p><b>{_('wiz_side_version', 'Version')}:</b> {version_text}</p>
            <p><b>{_('wiz_side_status', 'Status')}:</b> {status_text}</p>
            <hr style='border: 1px solid {hr_color};'>
            <p style='color: {desc_color};'>{desc}</p>
        </div>
        """
        if hasattr(self.ui, 'sidebarDesc'):
            self.ui.sidebarDesc.setHtml(rich_text)

    def open_app_website(self):
        if self.current_app_url:
            url = self.current_app_url[0] if isinstance(
                self.current_app_url, list) else self.current_app_url
            webbrowser.open(url)

    def eventFilter(self, source, event):
        if source == self.ui.DnDframe:
            if event.type() == QEvent.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                    return True
                return False

            elif event.type() == QEvent.Drop:
                urls = event.mimeData().urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    self.current_file_path = file_path
                    self.ui.filePathInput.setText(file_path)
                return True

        return super().eventFilter(source, event)

    def browse_file(self):
        """Opens a file dialog for selecting archive files."""
        path, selected_filter = QFileDialog.getOpenFileName(
            self.main_window,
            _("wiz_browse_title", "Select ZIP/7Z/PAF File"),
            "",
            "All Supported (*.zip *.7z *.paf *.paf.exe);;Archives (*.zip *.7z);;PortableApps (*.paf *.paf.exe)"
        )
        if path:
            self.current_file_path = path
            self.ui.filePathInput.setText(path)

    def start_install_from_button(self):
        """Initiates the installation process from the UI button."""
        path = getattr(self, 'current_file_path', None)
        if not path or not os.path.exists(path):
            path = self.ui.filePathInput.text().strip()

        if path and os.path.exists(path):
            self.start_wizard_flow(path)
        else:
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(_("wiz_err_title", "Error"))
            msg.setText(_("wiz_err_select_file",
                        "Please select a valid ZIP or 7Z file first!"))
            msg.setStyleSheet(self.get_msg_style())
            msg.exec_()

    def start_wizard_flow(self, file_path):
        """Analyzes the selected file and determines the installation flow."""
        self.current_file_path = file_path
        self.ui.filePathInput.setText(file_path)
        filename = os.path.basename(file_path)
        self.update_sidebar(filename, None, _("wiz_waiting", "Waiting..."))

        self.log(f"Analyzing file: {filename}...")

        if filename.lower().endswith('.paf') or filename.lower().endswith('.paf.exe'):
            self._handle_paf_flow(file_path)
        else:
            self._handle_zip_flow(file_path)

    def _handle_paf_flow(self, file_path):
        """Installation flow for .paf (PortableApps.com) files."""
        filename = os.path.basename(file_path)
        self.log("📦 PortableApps (.paf) file detected.")

        # Copy to staging area
        temp_paf_path = os.path.join(self.portable_root, filename)
        if os.path.abspath(file_path) != os.path.abspath(temp_paf_path):
            try:
                shutil.copy2(file_path, temp_paf_path)
                file_path = temp_paf_path
            except Exception as e:
                self.log(f"⚠️ Copy failed: {e}")

        self.log("🚀 Launching installer. Please complete the setup...")
        try:
            subprocess.run([file_path], check=True)
        except Exception as e:
            self.log(f"❌ Installation aborted or failed: {e}")
            if os.path.exists(temp_paf_path):
                os.remove(temp_paf_path)
            return

        if os.path.exists(temp_paf_path):
            os.remove(temp_paf_path)

        self.log("✅ Installation finished. Reading metadata...")
        folders = [os.path.join(self.portable_root, d) for d in os.listdir(self.portable_root)
                   if os.path.isdir(os.path.join(self.portable_root, d))]
        if not folders:
            return

        latest_folder = max(folders, key=os.path.getmtime)
        metadata = get_portable_apps_metadata(latest_folder)

        if metadata:
            app_name = metadata.get('name', 'Unknown')
            app_version = metadata.get('version', '1.0')
            start_exe_rel = metadata.get('start_exe')

            final_exe_path = None
            if start_exe_rel:
                potential_exe = os.path.join(latest_folder, start_exe_rel)
                if os.path.exists(potential_exe):
                    final_exe_path = os.path.abspath(potential_exe)

            if not final_exe_path:
                for f in os.listdir(latest_folder):
                    if f.lower().endswith('.exe'):
                        final_exe_path = os.path.abspath(
                            os.path.join(latest_folder, f))
                        break

            self.ui.appNameInput.setText(app_name)
            self.detected_version_regex = app_version
            self.ui.installButton.setProperty("final_version", app_version)
            self.ui.installButton.setProperty("paf_exe_path", final_exe_path)

            self.log(f"✨ Metadata: {app_name} v{app_version}")

            # Check scoop metadata directly
            scoop_data = None
            if is_internet_available():
                scoop_data = self.scoop.search_app(app_name)
                if not isinstance(scoop_data, dict):
                    scoop_data = None

            self.current_app_data = scoop_data
            scoop_ver = scoop_data.get('version') if scoop_data else None
            self.update_sidebar(app_name, scoop_data, app_version)

            self.log(
                f"📦 Auto-confirming version for PAF: {app_version}. Continuing...")
            latest_ver = scoop_ver if scoop_ver else app_version
            self._finalize_app_install(
                app_name, latest_folder, final_exe_path, app_version, latest_ver)
        else:
            self.log("⚠️ No metadata found in appinfo.ini.")

    def _handle_zip_flow(self, file_path):
        """Installation flow for .zip and .7z archives."""
        filename = os.path.basename(file_path)
        installer = AppInstaller(self.portable_root)
        if not installer.contains_exe(file_path):
            self.log(_("wiz_log_no_exe_err",
                     "ERROR: The file does not contain an executable (.exe)!"))
            return

        name_no_ext = re.sub(r'\.(zip|7z)$', '', filename, flags=re.I)
        ver_match = re.search(
            r'[-_\s]v?(\d+\.\d+(?:\.\d+)*)', name_no_ext, re.I)
        if ver_match:
            raw_name = name_no_ext[:ver_match.start()]
            self.detected_version_regex = ver_match.group(1)
        else:
            raw_name = name_no_ext
            self.detected_version_regex = ""

        raw_name = re.sub(
            r'(?i)[-_\s]*(portable|setup|installer|bin|x64|x86|win64)$', '', raw_name)
        detected_name = raw_name.replace("-", " ").replace("_", " ").title()

        self.update_sidebar(detected_name, None, _(
            "wiz_waiting", "Waiting..."))

        # 1. EXTRACT TO TEMP FOLDER FIRST
        self.log(_("wiz_log_extracting_to",
                 "Starting extraction to temporary folder..."))
        temp_target_name = detected_name + "_temp"
        temp_target = os.path.join(self.portable_root, temp_target_name)
        extracted_folder = installer.install_from_zip(
            self.current_file_path, temp_target_name)

        if not extracted_folder:
            self.log(_("wiz_err_extract_failed", "ERROR: Extraction failed."))
            return

        # 2. CHOCOLATEY SFX CHECK
        tools_dir = os.path.join(extracted_folder, "tools")
        if os.path.exists(tools_dir):
            file_32 = os.path.join(tools_dir, "7zip_x32.exe")
            file_64 = os.path.join(tools_dir, "7zip_x64.exe")

            if os.path.exists(file_32) or os.path.exists(file_64):
                self.log(
                    _("wiz_log_choc_sfx", "📦 Chocolatey SFX detected. Internal extraction with 7za..."))

                is_64bit = platform.machine().endswith(
                    '64') or os.environ.get("PROCESSOR_ARCHITEW6432")
                target_sfx = file_64 if (
                    is_64bit and os.path.exists(file_64)) else file_32

                if os.path.exists(target_sfx):
                    try:
                        seven_za_path = PathManager.get_bin_path("7za.exe")

                        if not seven_za_path:
                            raise FileNotFoundError(
                                _("wiz_err_no_7za", "7za.exe not found in project!"))

                        target_dir_abs = os.path.abspath(extracted_folder)
                        target_sfx_abs = os.path.abspath(target_sfx)

                        subprocess.run(
                            [seven_za_path, "x", target_sfx_abs, f"-o{target_dir_abs}", "-y"], check=True)

                        shutil.rmtree(tools_dir, ignore_errors=True)
                        self.log(_("wiz_log_internal_extract_ok",
                                 "✨ Internal extraction completed successfully!"))
                    except Exception as e:
                        self.log(_("wiz_log_internal_extract_err",
                                 "❌ Internal extraction error: {error}").format(error=e))

        # 3. FIND EXES & SORT
        self.log(_("wiz_log_searching_exes",
                 "Extraction finished. Searching for executables (.exe)..."))
        exes = []
        for root, subdirs, files in os.walk(extracted_folder):
            for f in files:
                if f.lower().endswith('.exe'):
                    exes.append(os.path.join(root, f))

        if not exes:
            self.log(_("wiz_err_no_exe_found",
                     "ERROR: No .exe files found in the archive!"))
            shutil.rmtree(extracted_folder, ignore_errors=True)
            return

        def sort_key(exe_path):
            fn = os.path.basename(exe_path).lower()
            if fn == "7zfm.exe":
                return 2
            if detected_name.lower().replace("++", "").replace(" ", "") in fn:
                return 1
            return 0

        exes.sort(key=sort_key, reverse=True)
        clean_names = [os.path.relpath(e, extracted_folder) for e in exes]

        # 4. GET PEFILE VERSION (New Feature)
        pe_version = get_pe_version(exes[0])
        if pe_version:
            self.log(f"🔎 Internal EXE Version found (pefile): {pe_version}")

        initial_ver = pe_version if pe_version else (
            self.detected_version_regex if self.detected_version_regex else "1.0")

        # 4.1 GET PEFILE NAME (New Feature)
        pe_name = get_pe_name(exes[0])
        if pe_name:
            self.log(f"🔎 Internal EXE Name found (pefile): {pe_name}")

        detected_name = pe_name if pe_name else detected_name
        self.ui.appNameInput.setText(detected_name)

        print(f"Detected Name: {detected_name}, PE Name: {pe_name}")

        # 5. SCOOP CHECK
        self.log(_("wiz_log_searching_scoop", "Searching Scoop for '{app_name}' info...").format(
            app_name=detected_name))
        scoop_data = None
        if is_internet_available():
            scoop_data = self.scoop.search_app(detected_name)
            if not isinstance(scoop_data, dict):
                scoop_data = None

        scoop_ver = scoop_data.get('version') if scoop_data else None
        self.current_app_data = scoop_data
        self.update_sidebar(detected_name, scoop_data, initial_ver)

        if scoop_ver:
            self.log(_("wiz_log_scoop_match", "Match found in Scoop (Version: {scoop_ver})").format(
                scoop_ver=scoop_ver))
        else:
            self.log(_("wiz_log_scoop_not_found",
                     "Application not found in Scoop API."))

        # 6. SHOW SINGLE UNIFIED DIALOG (New Feature)
        dialog = UnifiedInstallDialog(
            detected_name, initial_ver, clean_names, scoop_ver, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            final_name, final_version, final_exe_rel = dialog.get_data()

            # Rename Temp Folder to Final Name
            final_target = os.path.join(self.portable_root, final_name)
            if os.path.abspath(extracted_folder) != os.path.abspath(final_target):
                if os.path.exists(final_target):
                    shutil.rmtree(final_target, ignore_errors=True)
                os.rename(extracted_folder, final_target)
            else:
                final_target = extracted_folder

            final_exe_path = os.path.abspath(
                os.path.join(final_target, final_exe_rel))
            latest_ver = scoop_ver if scoop_ver else final_version

            self.ui.appNameInput.setText(final_name)
            self.ui.installButton.setProperty("final_version", final_version)

            self.log(_("wiz_log_version_set", "Version set: {final_version}").format(
                final_version=final_version))
            self._finalize_app_install(
                final_name, final_target, final_exe_path, final_version, latest_ver)
        else:
            self.log(_("wiz_log_install_cancelled",
                     "Installation cancelled by user."))
            shutil.rmtree(extracted_folder, ignore_errors=True)

    def _finalize_app_install(self, app_name, local_path, exe_path, version, latest_ver):
        """Handles database registration and shortcut creation."""
        source = "manual"
        url = ""
        homepage_url = ""

        if hasattr(self, 'current_app_data') and isinstance(self.current_app_data, dict):
            source = self.current_app_data.get('source', 'scoop')
            url = self.current_app_data.get('update_url', '')
            if not url and source == 'github':
                url = self.current_app_data.get(
                    'html_url', self.current_app_data.get('url', ''))
            homepage_url = self.current_app_data.get('homepage', '')

        self.db.add_or_update_app(
            name=app_name,
            local_path=local_path,
            exe_path=exe_path,
            source=source,
            update_url=url,
            current_version=version,
            latest_version=latest_ver,
            homepage=homepage_url
        )

        self.create_shortcut(app_name, exe_path)
        if hasattr(self.main_window, 'my_apps_controller'):
            self.main_window.my_apps_controller.refresh_data()

        if hasattr(self.main_window, 'activity_manager'):
            self.main_window.activity_manager.log(
                "wiz_act_install_success",
                event_type="install",
                params={"app_name": app_name, "version": version}
            )

        self.log(_("wiz_log_install_success",
                 "✅ Installation completed successfully!").format(app_name=app_name))

        msg = QMessageBox(self.main_window)
        msg.setStyleSheet(self.get_msg_style())
        msg.setWindowTitle(_("wiz_msg_success_title", "Success"))
        msg.setText(_("wiz_msg_success_text", "Application {app_name} is ready.").format(
            app_name=app_name))
        msg.exec_()

    def create_shortcut(self, name, absolute_exe_path):
        """Creates a Windows shortcut in the __Apps__ subdirectory."""
        try:

            apps_dir = os.path.abspath(
                os.path.join(self.portable_root, "__Apps__"))
            if not os.path.exists(apps_dir):
                os.makedirs(apps_dir)
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(
                os.path.join(apps_dir, f"{name}.lnk"))
            shortcut.TargetPath = absolute_exe_path
            shortcut.WorkingDirectory = os.path.dirname(absolute_exe_path)
            shortcut.save()
        except Exception as e:
            self.log(_("wiz_log_warn_shortcut_failed",
                     "⚠️ Warning: Shortcut not created ({error})").format(error=e))

    def start_quick_install(self, scoop_name):
        """Automated download and installation from Scoop or Chocolatey APIs."""
        if self._is_installing:
            self.log(_("wiz_log_already_running",
                     "⏳ An installation is already in progress. Please wait."))
            return

        self._is_installing = True
        save_path = ""
        nupkg_path = ""

        try:

            if hasattr(self.ui, 'consoleEdit'):
                self.ui.consoleEdit.clear()

            self.log(_("wiz_log_quick_start",
                     "--- STARTING QUICK INSTALL: {app_name} ---").format(app_name=scoop_name.upper()))

            app_data = self.smart_search_app(scoop_name)
            if not app_data:
                self.log(_("wiz_log_quick_err_no_data", "ERROR: No data found for '{app_name}'.").format(
                    app_name=scoop_name))
                return

            app_name = app_data.get('name', scoop_name.title())
            if scoop_name == "notepadplusplus":
                app_name = "Notepad++"

            version = app_data.get('version', '1.0')
            source = app_data.get('source', 'scoop')
            self.update_sidebar(app_name, app_data, _(
                "wiz_status_downloading", "Downloading..."))

            # Prepare expected hash for validation
            expected_hash = app_data.get('hash')
            if not expected_hash and app_data.get('architecture'):
                arch = app_data['architecture']
                if '64bit' in arch:
                    expected_hash = arch['64bit'].get('hash')
                elif '32bit' in arch:
                    expected_hash = arch['32bit'].get('hash')

            download_url = app_data.get('url')
            arch = app_data.get('architecture')
            if not download_url and arch:
                if '64bit' in arch:
                    download_url = arch['64bit'].get('url')
                elif '32bit' in arch:
                    download_url = arch['32bit'].get('url')

            if isinstance(download_url, list) and len(download_url) > 0:
                download_url = download_url[0]

            if not download_url:
                self.log(_("wiz_err_no_download_link",
                         "ERROR: No active download link found."))
                return

            if '#/' in download_url:
                download_url = download_url.split('#/')[0]

            downloads_dir = os.path.join(self.portable_root, "Downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)

            if source == "chocolatey":
                self.log(_("wiz_log_choc_downloading",
                         "📦 Fetching and analyzing Chocolatey package..."))
                nupkg_path = os.path.join(downloads_dir, f"{scoop_name}.nupkg")
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get(download_url, headers=headers, timeout=20)
                    r.raise_for_status()
                    with open(nupkg_path, 'wb') as f:
                        f.write(r.content)

                    real_url = None
                    with zipfile.ZipFile(nupkg_path, 'r') as z:
                        ps1_files = [f for f in z.namelist() if f.lower().endswith(
                            'chocolateyinstall.ps1')]
                        if ps1_files:
                            content = z.read(ps1_files[0]).decode(
                                'utf-8', errors='ignore')
                            match64 = re.search(
                                r"url64bit\s*=\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
                            match32 = re.search(
                                r"url\s*=\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
                            real_url = match64.group(1) if match64 else (
                                match32.group(1) if match32 else None)

                            # Extract Checksum from Chocolatey Script
                            match_hash = re.search(
                                r"checksum\s*=\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
                            if match_hash:
                                expected_hash = match_hash.group(1)

                    if real_url:
                        download_url = real_url
                        self.log(
                            _("wiz_log_official_url_found", "✅ Official Portable URL found: {url}").format(url=download_url))
                    else:
                        self.log(
                            _("wiz_log_checking_embedded", "📦 Checking for embedded files in nupkg..."))
                        embedded_zip = None
                        with zipfile.ZipFile(nupkg_path, 'r') as z:
                            zips = [f for f in z.namelist(
                            ) if f.lower().endswith('.zip')]
                            if zips:
                                embedded_zip = zips[0]
                                z.extract(embedded_zip, downloads_dir)
                                download_url = os.path.normpath(
                                    os.path.join(downloads_dir, embedded_zip))
                                self.log(_("wiz_log_embedded_zip_found", "✅ Embedded ZIP found: {zip_name}").format(
                                    zip_name=embedded_zip))

                        if not embedded_zip:
                            self.log(
                                _("wiz_log_direct_extract", "✅ Files located within nupkg. Direct extraction."))
                            download_url = nupkg_path

                except Exception as e:
                    self.log(
                        _("wiz_log_choc_err", "❌ Chocolatey error: {error}").format(error=e))
                    return

            final_ext = str(download_url).lower().split('?')[0]
            if final_ext.endswith('.exe') or final_ext.endswith('.msi'):
                self.log(_("wiz_err_security_installer_instead_of_zip",
                         "❌ SECURITY ERROR: Final file is an installer (.exe/.msi) instead of a .zip archive."))
                self.update_sidebar(app_name, None, _(
                    "wiz_status_error", "Error"))
                return

            if str(download_url).startswith("http"):
                file_name = download_url.split(
                    '/')[-1].split('?')[0].split('#/')[0]
                save_path = os.path.join(downloads_dir, file_name)
                self.log(_("wiz_log_download_final_start",
                         "Downloading final archive..."))

                try:
                    response = requests.get(
                        download_url, stream=True, timeout=20)
                    response.raise_for_status()

                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                QApplication.processEvents()
                    self.log(_("wiz_log_download_complete",
                             "Download complete!"))
                except Exception as e:
                    self.log(_("wiz_log_download_err",
                             "❌ Download error: {error}").format(error=e))
                    self.update_sidebar(app_name, None, _(
                        "wiz_status_error", "❌ Error"))
                    return
            else:
                save_path = download_url
                self.log(_("wiz_log_local_file",
                         "✅ File is already local, skipping download..."))

            # ==============================================================
            # ΕΛΕΓΧΟΣ ΑΚΕΡΑΙΟΤΗΤΑΣ CHECKSUM (HASH VALIDATION)
            # ==============================================================
            if expected_hash and os.path.exists(save_path) and not save_path.endswith('.nupkg'):
                clean_expected = str(expected_hash).strip().lower()
                if ":" in clean_expected:
                    clean_expected = clean_expected.split(":")[-1]

                # Αυτόματη ανίχνευση αλγορίθμου βάσει του μήκους του hash
                hash_len = len(clean_expected)
                algo_name = "SHA-256"
                if hash_len == 64:
                    hasher = hashlib.sha256()
                    algo_name = "SHA-256"
                elif hash_len == 40:
                    hasher = hashlib.sha1()
                    algo_name = "SHA-1"
                elif hash_len == 32:
                    hasher = hashlib.md5()
                    algo_name = "MD5"
                else:
                    hasher = hashlib.sha256()

                # --- ΕΜΦΑΝΙΣΗ ΣΤΗΝ ΚΟΝΣΟΛΑ ---
                self.log(_("wiz_log_security_check", "🔒 Checking integrity (Algorithm: {algo})...").format(
                    algo=algo_name))
                self.log(_("wiz_log_expected_hash", "📋 Expected Hash (Online API): {hash_val}").format(
                    hash_val=clean_expected))

                # Υπολογισμός του Hash του αρχείου που κατεβάσαμε
                with open(save_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(8192), b""):
                        hasher.update(byte_block)
                calculated_hash = hasher.hexdigest().lower()

                # --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΟΣ ΣΤΗΝ ΚΟΝΣΟΛΑ ---
                self.log(_("wiz_log_calculated_hash", "🧮 Calculated Hash (Local File): {hash_val}").format(
                    hash_val=calculated_hash))

                if calculated_hash != clean_expected:
                    self.log(_("wiz_err_checksum_mismatch",
                             "❌ ΚΡΙΣΙΜΟ ΣΦΑΛΜΑ ΑΣΦΑΛΕΙΑΣ: Τα Checksums ΔΕΝ ταιριάζουν! Η εγκατάσταση ακυρώθηκε."))
                    self.update_sidebar(app_name, None, _(
                        "wiz_status_hash_error", "❌ Hash Error"))
                    return
                else:
                    self.log(
                        _("wiz_log_hash_success", "✅ Integrity check passed! Hashes match."))
            elif not expected_hash:
                self.log(_("wiz_log_warn_no_checksum",
                         "⚠️ Warning: No checksum found in API. Skipping check."))

            # 5. Αποσυμπίεση
            self.log(_("wiz_log_extracting_7zip", "Αποσυμπίεση με το 7-Zip..."))
            installer = AppInstaller(self.portable_root)
            extracted_folder = installer.install_from_zip(save_path, app_name)

            if not extracted_folder:
                self.log(_("wiz_err_extract_failed",
                         "❌ Extraction failed."))
                return

            # =================================================================
            # 🛡️ ΑΥΤΟΜΑΤΟΣ ΜΗΧΑΝΙΣΜΟΣ EXTRACTION ΣΤΟΝ ΚΕΝΤΡΙΚΟ ΦΑΚΕΛΟ 7ZIP
            # =================================================================
            tools_dir = os.path.join(extracted_folder, "tools")
            if os.path.exists(tools_dir):
                file_32 = os.path.join(tools_dir, "7zip_x32.exe")
                file_64 = os.path.join(tools_dir, "7zip_x64.exe")

                if os.path.exists(file_32) or os.path.exists(file_64):
                    self.log(_("wiz_log_choc_container_found",
                             "📦 Chocolatey container found. Performing clean SFX extraction..."))
                    print(_("wiz_console_7za_extract",
                          "\n🚀 [FLOWDECK] Extraction του 7-Zip με 7za!"))

                    # Επιλογή 64-bit ή 32-bit ανάλογα με το σύστημα
                    is_64bit = platform.machine().endswith(
                        '64') or os.environ.get("PROCESSOR_ARCHITEW6432")
                    target_sfx = file_64 if (
                        is_64bit and os.path.exists(file_64)) else file_32

                    if os.path.exists(target_sfx):
                        try:
                            # Χρήση του PathManager για το 7za.exe
                            seven_za_path = PathManager.get_bin_path("7za.exe")

                            if not seven_za_path:
                                raise FileNotFoundError(
                                    _("wiz_err_7za_not_found", "The 7za.exe was not found in the project!"))

                            print(_("wiz_console_7za_found", "🎯 The 7za.exe was found at: {path}").format(
                                path=seven_za_path))

                            # 2. ΑΠΟΣΥΜΠΙΕΣΗ ΚΑΤΕΥΘΕΙΑΝ ΣΤΟΝ ΦΑΚΕΛΟ 7ZIP
                            target_dir_abs = os.path.abspath(extracted_folder)
                            target_sfx_abs = os.path.abspath(target_sfx)
                            print(_("wiz_console_sfx_unzipping", "📦 Unzipping του {file_name} στον κεντρικό φάκελο: {dest_dir}").format(
                                file_name=os.path.basename(target_sfx),
                                dest_dir=target_dir_abs
                            ))

                            subprocess.run(
                                [seven_za_path, "x", target_sfx_abs, f"-o{target_dir_abs}", "-y"], check=True)
                            print(
                                _("wiz_console_sfx_success", "✅ The SFX extraction completed successfully!"))

                            # 3. ΚΑΘΑΡΙΣΜΟΣ: Σβήνουμε τελείως τον φάκελο tools
                            shutil.rmtree(tools_dir, ignore_errors=True)
                            self.log(_("wiz_log_internal_extract_success",
                                     "✨ The internal extraction completed and the tools folder was cleaned!"))
                        except Exception as e:
                            self.log(
                                _("wiz_log_extract_err", "❌ Error occurred during extraction: {error}").format(error=e))
                            print(_("wiz_console_extract_fail", "❌ EXTRACTION FAILED WITH 7ZA: {error}").format(
                                error=e))
            print("==================================================\n")
            # =================================================================

            final_exe_path = None
            target_exe = app_data.get('bin')

            if isinstance(target_exe, list) and len(target_exe) > 0:
                target_exe = target_exe[0]
                if isinstance(target_exe, list):
                    target_exe = target_exe[0]

            all_exes = []
            for root, subdirs, files in os.walk(extracted_folder):
                for f in files:
                    if f.lower().endswith('.exe'):
                        all_exes.append(os.path.abspath(os.path.join(root, f)))

            # Priority 1: 7-Zip GUI
            for exe_p in all_exes:
                if os.path.basename(exe_p).lower() == "7zfm.exe":
                    final_exe_path = exe_p
                    break

            # Priority 2: API recommended binary
            if not final_exe_path and target_exe and isinstance(target_exe, str):
                potential_path = os.path.join(extracted_folder, target_exe)
                if os.path.exists(potential_path):
                    final_exe_path = os.path.abspath(potential_path)

            # Priority 3: Fuzzy name match
            if not final_exe_path and all_exes:
                for exe_p in all_exes:
                    if app_name.lower().replace("++", "").replace(" ", "") in os.path.basename(exe_p).lower():
                        final_exe_path = exe_p
                        break

                # Fallback: First available binary
                if not final_exe_path and all_exes:
                    final_exe_path = all_exes[0]

            if final_exe_path:
                source = app_data.get('source', 'scoop')
                url = app_data.get('update_url', '')
                if not url and source == 'github':
                    url = app_data.get('html_url', app_data.get('url', ''))

                homepage_url = app_data.get('homepage', '') if app_data else ''

                self.db.add_or_update_app(
                    name=app_name,
                    local_path=extracted_folder,
                    exe_path=final_exe_path,
                    source=source,
                    update_url=url,
                    current_version=version,
                    latest_version=version,
                    homepage=homepage_url
                )

                self.create_shortcut(app_name, final_exe_path)
                if hasattr(self.main_window, 'my_apps_controller'):
                    self.main_window.my_apps_controller.refresh_data()
                self.log(_("wiz_log_success_simple", "✅ Success! {app_name} has been installed.").format(
                    app_name=app_name))
                self.update_sidebar(app_name, app_data, version)

                if hasattr(self.main_window, 'activity_manager'):
                    print(f"DEBUG: Logging install success for {app_name}")

                    self.main_window.activity_manager.log(
                        "wiz_act_install_success",
                        event_type="install",
                        params={"app_name": app_name, "version": version}
                    )

                msg = QMessageBox(self.main_window)

                msg.setStyleSheet(self.get_msg_style())
                msg.setWindowTitle(_("wiz_msg_success_title", "Success!"))
                msg.setText(_("wiz_msg_install_success",
                            "{name} installed successfully!").format(name=app_name))
                msg.exec_()
            else:
                self.log(
                    _("wiz_err_no_exe_found_after_extract", "ERROR: No executable (.exe) found after extraction!"))

        finally:
            # Cleanup temporary files
            try:
                if save_path and os.path.exists(save_path):
                    os.remove(save_path)
                    self.log(_("wiz_log_cleanup_success", "🧹 Cleanup: Downloaded file {filename} was deleted.").format(
                        filename=os.path.basename(save_path)))
                if nupkg_path and os.path.exists(nupkg_path):
                    os.remove(nupkg_path)
            except Exception as e:
                print(f"Post-install cleanup error: {e}")

            self._is_installing = False
