# Standard Library Imports
import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
import zipfile

# Third-Party Library Imports
import requests
from PyQt5.QtCore import QThread, pyqtSignal

# Local Module Imports
from locales.localization import _

logger = logging.getLogger(__name__)


class UpdateDownloaderWorker(QThread):
    """
    Background worker thread to download the update zip file,
    verify its SHA-256 checksum, extract it safely, and prepare the config file.
    Progress bar is split into 0-50% for download and 50-100% for extraction.
    """

    # Signals for UI communication
    progress = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, download_url, expected_hash, target_dir, exe_name, new_version="latest"):
        super().__init__()
        self.download_url = download_url
        self.expected_hash = expected_hash.lower() if expected_hash else None
        self.target_dir = target_dir
        self.exe_name = exe_name
        self.new_version = new_version
        self.is_cancelled = False

    def cancel(self):
        """Method to trigger worker cancellation from the UI."""
        self.is_cancelled = True

    def run(self):
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, "flowdeck_update.zip")
        base_extract_dir = os.path.join(temp_dir, "flowdeck_extracted")

        try:
            # Step 1: Prepare temporary storage paths
            if os.path.exists(base_extract_dir):
                self._safe_remove_path(base_extract_dir)
            os.makedirs(base_extract_dir, exist_ok=True)

            # Step 2: Download the Zip file with progress tracking (Scaled 0% - 50%)
            self.status_changed.emit(
                _("upd_status_downloading_update", "Downloading update..."))

            response = requests.get(self.download_url, stream=True, timeout=10)
            response.raise_for_status()

            total_length = response.headers.get("content-length")

            with open(zip_path, "wb") as file:
                if total_length is None:
                    file.write(response.content)
                    self.progress.emit(50)
                else:
                    downloaded = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        if self.is_cancelled:
                            file.close()
                            response.close()  # Close network stream handle
                            break
                        downloaded += len(data)
                        file.write(data)
                        # Scale download progress to 0% - 50%
                        download_percentage = int(
                            (downloaded / total_length) * 50)
                        self.progress.emit(download_percentage)

            # Check if download was cancelled after closing file handles
            if self.is_cancelled:
                self._safe_remove_path(zip_path)
                self._safe_remove_path(base_extract_dir)
                self.finished.emit(
                    False, _("upd_download_cancelled_msg", "Download cancelled by user."))
                return

            # Step 3: SHA-256 Digest Verification
            if self.expected_hash:
                self.status_changed.emit(
                    _("upd_status_verifying_integrity", "Verifying file integrity..."))
                sha256_hash = hashlib.sha256()
                with open(zip_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)

                downloaded_hash = sha256_hash.hexdigest().lower()

                if downloaded_hash != self.expected_hash:
                    self._safe_remove_path(zip_path)
                    self._safe_remove_path(base_extract_dir)
                    error_msg = _(
                        "upd_checksum_failed_msg",
                        "Checksum verification failed!\nExpected: {expected}\nGot: {got}"
                    ).format(expected=self.expected_hash, got=downloaded_hash)
                    self.finished.emit(False, error_msg)
                    logger.error(
                        f"Checksum verification failed!\n\tExpected: {self.expected_hash}\n\tGot: {downloaded_hash}")
                    return

            # Step 4: Extract the Zip file safely with progress tracking (Scaled 50% - 100%)
            self.status_changed.emit(
                _("upd_status_extracting_files", "Extracting files..."))

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                members = zip_ref.infolist()
                total_files = len(members)

                for index, member in enumerate(members, start=1):
                    if self.is_cancelled:
                        break

                    # Secure extraction path to prevent Zip Slip vulnerability
                    target_path = os.path.abspath(
                        os.path.join(base_extract_dir, member.filename))
                    if not target_path.startswith(os.path.abspath(base_extract_dir)):
                        continue

                    if member.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(
                            target_path), exist_ok=True)
                        with zip_ref.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)

                    # Scale extraction progress to 50% - 100%
                    if total_files > 0:
                        extract_percentage = 50 + \
                            int((index / total_files) * 50)
                        self.progress.emit(extract_percentage)

            # Check if extraction was cancelled after closing zip handle
            if self.is_cancelled:
                self._safe_remove_path(zip_path)
                self._safe_remove_path(base_extract_dir)
                self.finished.emit(
                    False, _("upd_extraction_cancelled_msg", "Extraction cancelled by user."))
                return

            # Clean up downloaded zip file after successful extraction
            self._safe_remove_path(zip_path)

            # Step 5: Determine effective extraction directory
            extracted_items = os.listdir(base_extract_dir)
            effective_dir = base_extract_dir
            if len(extracted_items) == 1:
                single_item_path = os.path.join(
                    base_extract_dir, extracted_items[0])
                if os.path.isdir(single_item_path):
                    effective_dir = single_item_path

            # Step 6: Write update_config.json in the effective extracted directory
            config_data = {
                "source_dir": effective_dir,
                "target_dir": self.target_dir,
                "exe_name": self.exe_name,
                "version": self.new_version
            }
            config_path = os.path.join(effective_dir, "update_config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)

            self.progress.emit(100)
            self.finished.emit(True, effective_dir)

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error during update download: {req_err}")
            self._safe_remove_path(zip_path)
            self._safe_remove_path(base_extract_dir)
            self.finished.emit(
                False,
                _("upd_no_internet_text",
                  "No internet connection detected.\nPlease check your connection and try again.")
            )

        except zipfile.BadZipFile as zip_err:
            logger.error(
                f"Downloaded zip file is invalid or corrupt: {zip_err}")
            self._safe_remove_path(zip_path)
            self._safe_remove_path(base_extract_dir)
            self.finished.emit(
                False,
                _("wiz_invalid_file_msg",
                  "The file does not appear to be a Portable App.")
            )

        except Exception as e:
            logger.error(f"Unexpected error in UpdateDownloaderWorker: {e}")
            self._safe_remove_path(zip_path)
            self._safe_remove_path(base_extract_dir)
            self.finished.emit(False, str(e))

    def _safe_remove_path(self, path, retries=5, delay=1):
        """
        Safely removes a file or directory using a retry loop to prevent WinError 32 
        when process handles are releasing asynchronously.
        """
        for i in range(retries):
            try:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        os.remove(path)
                return True
            except Exception:
                time.sleep(delay)
        logger.warning(
            f"Failed to remove temporary path after retries: {path}")
        return False
