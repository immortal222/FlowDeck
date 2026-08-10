import logging
from PyQt5.QtCore import QThread, pyqtSignal

from core.services.version_fetcher import VersionMetadataFetcher

logger = logging.getLogger(__name__)


class UpdateCheckWorker(QThread):
    """Worker thread that checks for application updates across various sources.

    The heavy-lifting of contacting APIs is delegated to ``VersionMetadataFetcher``
    so this QThread remains a thin concurrency wrapper that emits a structured
    result dict via signals for the rest of the application to consume.
    """

    app_checked = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, apps_list, db):
        super().__init__()
        self.apps_list = apps_list
        self.db = db
        self.fetcher = VersionMetadataFetcher()

    def run(self):
        """Executes the update check logic for each application in the provided list."""
        logger.debug(f"Thread started. Processing {len(self.apps_list)} apps.")

        for app in self.apps_list:
            name = app.get("name", "")
            source = app.get("source", "manual")
            url = app.get("update_url", "")

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

            current_ver = normalize_version(
                app.get("current_version") or app.get("ver"))
            homepage = app.get("homepage", "")
            logger.debug(
                f"Checking {name} (Source: {source}, Current: {current_ver or 'unknown'})")

            has_update = False
            latest_ver = current_ver
            error = None

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
                    if latest_norm != current_ver:
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
