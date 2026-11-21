# Standard Library Imports
import logging
import os

# Third-Party Library Imports
from PyQt5.QtCore import QThread, pyqtSignal

# Local Module Imports
from core.services.version_fetcher import VersionMetadataFetcher
from core.utils import get_pe_version, is_update_available, resolve_paf_metadata

logger = logging.getLogger(__name__)


class UpdateCheckWorker(QThread):
    """Worker thread that checks for application updates across various sources.

    The heavy-lifting of contacting APIs is delegated to ``VersionMetadataFetcher``
    so this QThread remains a thin concurrency wrapper that emits a structured
    result dict via signals for the rest of the application to consume.
    """

    app_checked = pyqtSignal(object)
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal()

    def __init__(self, apps_list, db):
        super().__init__()
        self.apps_list = apps_list
        self.db = db
        self.fetcher = VersionMetadataFetcher()

    def run(self):
        """Executes the update check logic for each application in the provided list."""
        total_apps = len(self.apps_list)
        logger.debug(f"Thread started. Processing {total_apps} apps.")

        # Helper function defined once outside the loop for efficiency
        def normalize_version(value):
            if value is None:
                return None
            text = str(value).strip().lower()
            if not text or text in {"", "none", "unknown", "n/a", "-"}:
                return None
            text = text.lstrip('v')
            if text.count('.') == 3 and text.endswith('.0'):
                text = text.removesuffix('.0')
            return text

        for index, app in enumerate(self.apps_list, start=1):
            name = app.get("name", "")
            # Emit current progress before starting the network check
            self.progress.emit(index, total_apps, name)
            source = app.get("source", "manual")
            url = app.get("update_url", "")
            install_method = app.get("install_method", "unknown")
            local_path = app.get("local_path", "")
            exe_path = app.get("exe_path", "")

            current_ver = normalize_version(
                app.get("current_version") or app.get("ver"))
            homepage = app.get("homepage", "")
            logger.debug(
                f"Checking {name} (Source: {source}, Current: {current_ver or 'unknown'})")

            has_update = False
            latest_ver = current_ver
            error = None

            # Resolve actual local version (PAF vs Non-PAF)
            resolved_local_ver = None

            if install_method == "paf" and local_path and os.path.exists(local_path):
                paf_meta = resolve_paf_metadata(local_path)
                if paf_meta and paf_meta.get("version"):
                    resolved_local_ver = normalize_version(
                        paf_meta.get("version"))
            elif exe_path and os.path.isfile(exe_path):
                resolved_local_ver = normalize_version(
                    get_pe_version(exe_path))

            # Sync local database if disk version differs from database record
            if resolved_local_ver and resolved_local_ver != current_ver:
                logger.info(
                    f"Detected updated local version for {name}: {current_ver} -> {resolved_local_ver}"
                )
                current_ver = resolved_local_ver
                try:
                    self.db.update_current_version(name, current_ver)
                except Exception as e:
                    logger.error(
                        f"Failed to update current version in DB for {name}: {e}"
                    )

            try:
                result = self.fetcher.fetch(name, source, url)

                # Handle server-level failures signalled by the fetcher
                if result.get("server_error"):
                    logger.warning(
                        f"Skipping {name} database update due to remote server error.")
                    continue

                latest_ver = result.get("latest_version")
                if result.get("homepage"):
                    homepage = result.get("homepage")

                latest_norm = normalize_version(latest_ver)
                if latest_norm is None or current_ver is None:
                    latest_ver = latest_norm
                else:
                    # Use numerical/smart version comparison instead of simple inequality
                    if is_update_available(current_ver, latest_norm):
                        has_update = True
                    latest_ver = latest_norm

            except Exception as e:
                error = str(e)
                logger.warning(f"ERROR checking updates for {name}: {e}")
                logger.warning(
                    f"Online update check failed for {name} ({source}): {e}")

            # Persist latest version metadata to the database
            try:
                self.db.update_latest_version(name, latest_ver, homepage)
            except Exception as e:
                logger.error(
                    f"Failed to write latest version to DB for {name}: {e}")

            update_result = {
                "name": name,
                "source": source,
                "current_version": current_ver,
                "latest_version": latest_ver,
                "homepage": homepage,
                "has_update": has_update,
                "error": error,
            }
            self.app_checked.emit(update_result)

        self.finished.emit()
