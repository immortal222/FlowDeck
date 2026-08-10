import logging
import os
import shutil

logger = logging.getLogger(__name__)


class DatabaseRecoveryService:
    """Handles recovery decisions for a missing or corrupted database."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.backups_dir = os.path.join(os.path.dirname(db_path), "backups")

    def restore_from_latest_backup(self):
        if not os.path.exists(self.backups_dir):
            logger.warning("Backup directory not found.")
            return False

        backups = [f for f in os.listdir(
            self.backups_dir) if f.endswith(".db")]
        if not backups:
            logger.warning("No backups available in the directory.")
            return False

        latest_backup = sorted(backups)[-1]
        backup_full_path = os.path.join(self.backups_dir, latest_backup)

        try:
            corrupted_copy = self.db_path + ".corrupted"
            if os.path.exists(self.db_path):
                if os.path.exists(corrupted_copy):
                    os.remove(corrupted_copy)
                os.rename(self.db_path, corrupted_copy)

            shutil.copy2(backup_full_path, self.db_path)
            logger.info(
                f"Database successfully restored from backup: {latest_backup}")
            return True
        except Exception as exc:
            logger.error(f"Failed to restore from backup: {exc}")
            return False
