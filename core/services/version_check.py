# Standard Library Imports
import logging

# Third-Party Library Imports
from packaging.version import parse as parse_version
from PyQt5.QtCore import QThread, pyqtSignal
import requests

# Local Application Imports
from locales.localization import _

logger = logging.getLogger(__name__)


def check_github_updates(username="immortal222", repo="FlowDeck", current_version="0.1.0"):
    """
    Checks the API (local or GitHub) for the latest release metadata,
    including version, download URL, and SHA-256 digest.

    :param username: str - GitHub username or organization
    :param repo: str - Name of the repository
    :param current_version: str - Current application version
    """
    # For local testing via XAMPP, targeting local mock API JSON endpoint
    # url = "http://localhost/mock_release.json"
    # Production endpoint alternative:
    url = f"https://api.github.com/repos/{username}/{repo}/releases/latest"

    headers = {'User-Agent': 'Python-Update-Checker'}

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            remote_tag = data.get("tag_name", "")
            latest_version = remote_tag.lstrip('v')

            if parse_version(latest_version) > parse_version(current_version):
                download_url = None
                digest = None

                # Locate the zip asset and extract its download URL and digest
                assets = data.get("assets", [])
                for asset in assets:
                    asset_name = asset.get("name", "")
                    if asset_name.endswith(".zip"):
                        download_url = asset.get("browser_download_url")
                        # Strip "sha256:" prefix if present in the digest field
                        raw_digest = asset.get("digest", "")
                        if raw_digest and raw_digest.startswith("sha256:"):
                            digest = raw_digest.replace("sha256:", "")
                        else:
                            digest = raw_digest
                        break

                update_info = {
                    "version": latest_version,
                    "title": data.get("name"),
                    "changelog": data.get("body"),
                    "html_url": data.get("html_url"),
                    "download_url": download_url,
                    "digest": digest
                }
                logger.info(
                    f"Update available: {latest_version} (Current: {current_version})")
                return True, update_info, None
            else:
                return False, None, None

        elif response.status_code == 404:
            logger.warning("Release metadata was not found.")
            return False, None, _("upd_error_title", "Error")
        else:
            logger.error(
                f"Error checking updates: HTTP {response.status_code}")
            return False, None, _("upd_title_error", "Network Error")

    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error: {e}")
        return False, None, _("upd_no_server_text", "Unable to connect to the update server.\nPlease ensure the server is active and try again.")
    except Exception as e:
        logger.error(f"Unexpected error during version check: {e}")
        return False, None, str(e)


# Στην κλάση VersionCheckWorker:

class VersionCheckWorker(QThread):
    """
    Worker thread to execute version check asynchronously without blocking the UI.
    Signals:
        finished: Emits (has_update: bool, update_info: dict|None, error_msg: str|None)
    """
    finished = pyqtSignal(bool, object, str)

    def __init__(self, username="immortal222", repo="FlowDeck", current_version="0.1.0", parent=None):
        super().__init__(parent)
        self.username = username
        self.repo = repo
        self.current_version = current_version

    def run(self):
        is_available, update_info, error_msg = check_github_updates(
            username=self.username,
            repo=self.repo,
            current_version=self.current_version
        )
        self.finished.emit(is_available, update_info, error_msg)
