import logging

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from core.api.scoop_api import ScoopAPI
from core.api.chocolatey_api import ChocolateyAPI

logger = logging.getLogger(__name__)


class UpdateCheckWorker(QThread):
    """Worker thread that checks for application updates across various sources (GitHub, Scoop, Chocolatey)."""

    app_checked = pyqtSignal(str, bool, str)
    finished = pyqtSignal()

    def __init__(self, apps_list, db):
        super().__init__()
        self.apps_list = apps_list
        self.db = db
        self.scoop = ScoopAPI()
        self.choco = ChocolateyAPI()

    def run(self):
        """Executes the update check logic for each application in the provided list."""
        print(
            f"[DEBUG-Worker] Thread started. Processing {len(self.apps_list)} apps.")

        for app in self.apps_list:
            name = app.get("name", "")
            source = app.get("source", "manual")
            url = app.get("update_url", "")

            # Normalize current version string
            current_ver = str(app.get("current_version", "1.0")
                              ).strip().lower().lstrip('v')
            homepage = app.get("homepage", "")
            print(
                f"[DEBUG-Worker] Checking {name} (Source: {source}, Current: {current_ver})")

            has_update = False
            latest_ver = current_ver

            try:
                # 1. Check GitHub Releases
                if source == "github" and url:
                    repo = url.replace("https://github.com/", "").strip("/")
                    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                    resp = requests.get(api_url, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        latest_ver = data.get(
                            "tag_name", current_ver).strip().lower().lstrip('v')
                        if latest_ver != current_ver:
                            has_update = True

                # 2. Check Chocolatey API
                elif source == "chocolatey":
                    search_term = name.lower().replace(" ", "").replace("++", "plusplus")
                    choco_data = self.choco.search_app(search_term)

                    if choco_data == "SERVER_ERROR":
                        logger.warning(
                            f"Skipping {name} database update due to Chocolatey server error.")
                        continue

                    if choco_data and choco_data.get('version'):
                        latest_ver = str(choco_data.get(
                            'version')).strip().lower().lstrip('v')
                        print(
                            f"[DEBUG-Worker] Chocolatey API returned v{latest_ver} for {name}")
                        if choco_data.get('homepage'):
                            homepage = choco_data.get('homepage')
                        if latest_ver != current_ver:
                            has_update = True
                    else:
                        # Fallback to None if not found online
                        latest_ver = None

                # 3. Check Scoop API
                elif source == "scoop" or (not source or source == "manual"):
                    scoop_data = self.scoop.search_app(name)

                    if scoop_data == "SERVER_ERROR":
                        logger.warning(
                            f"Skipping {name} database update due to Scoop server error.")
                        continue

                    if scoop_data and scoop_data.get('version'):
                        latest_ver = str(scoop_data.get(
                            'version')).strip().lower().lstrip('v')
                        print(
                            f"[DEBUG-Worker] Scoop API returned v{latest_ver} for {name}")
                        if scoop_data.get('homepage'):
                            homepage = scoop_data.get('homepage')
                        if latest_ver != current_ver:
                            has_update = True
                    else:
                        # Fallback to None if not found online
                        latest_ver = None

            except Exception as e:
                print(f"[DEBUG-Worker] ERROR checking updates for {name}: {e}")
                logger.warning(
                    f"Online update check failed for {name} ({source}): {e}")

            # Persist latest version metadata to the database
            try:
                self.db.update_latest_version(name, latest_ver, homepage)
            except Exception as e:
                logger.error(
                    f"Failed to write latest version to DB for {name}: {e}")

            self.app_checked.emit(name, has_update, latest_ver)

        self.finished.emit()
