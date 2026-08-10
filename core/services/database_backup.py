import logging
import os
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseBackupService:
    """Handles database backup creation and old backup cleanup."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.backups_dir = os.path.join(os.path.dirname(db_path), "backups")

    def has_backups(self):
        if not os.path.exists(self.backups_dir):
            return False
        backups = [f for f in os.listdir(
            self.backups_dir) if f.endswith(".db")]
        return len(backups) > 0

    def create_backup(self):
        os.makedirs(self.backups_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dest = os.path.join(
            self.backups_dir, f"flowdeck_backup_{timestamp}.db")

        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_dest)
                logger.info(f"Backup created: {backup_dest}")
                self._cleanup_old_backups()
                return True
        except Exception as exc:
            logger.error(f"Failed to create backup: {exc}")
        return False

    def _cleanup_old_backups(self):
        try:
            backups = sorted([f for f in os.listdir(
                self.backups_dir) if f.endswith(".db")])
            while len(backups) > 5:
                oldest = backups.pop(0)
                os.remove(os.path.join(self.backups_dir, oldest))
                logger.info(f"Removed old backup: {oldest}")
        except Exception as exc:
            logger.error(f"Error cleaning up old backups: {exc}")
