import logging
import os
import sqlite3

from core.services.database_backup import DatabaseBackupService
from core.services.database_recovery import DatabaseRecoveryService
from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Thin facade around SQLite persistence, schema initialization, and recovery."""

    def __init__(self, db_name="flowdeck.db", backup_service=None, recovery_service=None):
        self.db_path = PathManager.get_database_path(db_name)
        self.backup_service = backup_service or DatabaseBackupService(
            self.db_path)
        self.recovery_service = recovery_service or DatabaseRecoveryService(
            self.db_path)
        self._ensure_database_health()
        self.create_tables()

    def _ensure_database_health(self):
        if not os.path.exists(self.db_path):
            if self.backup_service.has_backups():
                logger.info(
                    "Database file missing. Attempting recovery from backup.")
                self.recovery_service.restore_from_latest_backup()
        elif self.is_corrupted():
            logger.error(
                "Database file is corrupted. Starting automatic restoration...")
            self.recovery_service.restore_from_latest_backup()

    def get_connection(self):
        """Returns a new sqlite3 connection."""
        return sqlite3.connect(self.db_path)

    def is_corrupted(self):
        """Checks if the database file is valid and passes integrity checks."""
        if not os.path.exists(self.db_path):
            return False

        if os.path.getsize(self.db_path) == 0:
            return True

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            return not (result and result[0] == "ok")
        except Exception as e:
            logger.error(f"Critical error during integrity check: {e}")
            return True
        finally:
            if conn:
                conn.close()

    def has_backups(self):
        """Checks for existing backup files in the backup directory."""
        return self.backup_service.has_backups()

    def create_backup(self):
        """Creates a timestamped backup and triggers old backup cleanup."""
        return self.backup_service.create_backup()

    def restore_from_latest_backup(self):
        """Restores the database from the most recent backup file."""
        return self.recovery_service.restore_from_latest_backup()

    def create_tables(self):
        """Initializes the database schema."""
        query = """
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            local_path TEXT NOT NULL,
            exe_path TEXT NOT NULL,
            source TEXT DEFAULT 'manual',
            update_url TEXT,
            current_version TEXT DEFAULT '1.0',
            latest_version TEXT DEFAULT NULL,
            homepage TEXT DEFAULT '',
            is_favorite INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    def add_or_update_app(self, name, local_path, exe_path, source="manual", update_url="", current_version="1.0", latest_version=None, homepage=""):
        """Inserts or updates an application entry with relative paths if inside app root."""
        # Convert absolute paths to relative before writing to database
        rel_local_path = PathManager.to_relative_path(local_path)
        rel_exe_path = PathManager.to_relative_path(exe_path)

        query = """
        INSERT INTO apps (name, local_path, exe_path, source, update_url, current_version, latest_version, homepage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            local_path=excluded.local_path,
            exe_path=excluded.exe_path,
            source=excluded.source,
            update_url=excluded.update_url,
            current_version=excluded.current_version,
            latest_version=excluded.latest_version,
            homepage=excluded.homepage
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, rel_local_path, rel_exe_path,
                               source, update_url, current_version, latest_version, homepage))
                conn.commit()
                return True
        except Exception as e:
            logger.error(
                f"Failed to write {name} to the database.", exc_info=True)
            return False

    def get_all_apps(self):
        """Retrieves all applications and resolves paths to absolute in memory."""
        query = "SELECT * FROM apps ORDER BY name COLLATE NOCASE ASC"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                results = []
                for row in cursor.fetchall():
                    app_dict = dict(row)
                    # Convert relative paths stored in DB to absolute paths in memory
                    app_dict['local_path'] = PathManager.to_absolute_path(
                        app_dict.get('local_path', ''))
                    app_dict['exe_path'] = PathManager.to_absolute_path(
                        app_dict.get('exe_path', ''))
                    results.append(app_dict)
                return results
        except Exception as e:
            logger.error(f"Error retrieving applications: {e}")
            return []

    def get_app_by_name(self, name):
        """Retrieves metadata for a specific application and resolves paths to absolute in memory."""
        query = "SELECT * FROM apps WHERE name = ?"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                row = cursor.fetchone()
                if row:
                    app_dict = dict(row)
                    app_dict['local_path'] = PathManager.to_absolute_path(
                        app_dict.get('local_path', ''))
                    app_dict['exe_path'] = PathManager.to_absolute_path(
                        app_dict.get('exe_path', ''))
                    return app_dict
                return None
        except Exception as e:
            logger.error(f"Error retrieving application {name}: {e}")
            return None

    def delete_app(self, name):
        """Removes an application from the database."""
        query = "DELETE FROM apps WHERE name = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting application {name}: {e}")
            return False

    def increment_usage(self, name):
        """Increments the usage counter for an application."""
        query = "UPDATE apps SET usage_count = usage_count + 1 WHERE name = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error incrementing usage count for {name}: {e}")

    def update_latest_version(self, name, latest_version, homepage=""):
        """Updates the latest available version and homepage URL for an application."""
        query = "UPDATE apps SET latest_version = ?, homepage = ? WHERE name = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (latest_version, homepage, name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(
                f"Error updating latest version for {name}: {e}")
            return False

    def toggle_favorite(self, app_id, status):
        """Toggles the favorite status of an application. Adds the column if it doesn't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE apps SET is_favorite = ? WHERE id = ?", (status, app_id))
                conn.commit()
                logger.info(
                    f"is_favorite for ID {app_id} changed to {status}")

        except Exception as e:
            error_msg = str(e).lower()
            if "no such column: is_favorite" in error_msg or "has no column" in error_msg:
                logger.warning(
                    "Column 'is_favorite' missing. Adding it automatically...")
                try:
                    with self.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "ALTER TABLE apps ADD COLUMN is_favorite INTEGER DEFAULT 0")
                        cursor.execute(
                            "UPDATE apps SET is_favorite = ? WHERE id = ?", (status, app_id))
                        conn.commit()
                        logger.info(
                            f"Success after schema update: is_favorite changed to {status}")
                except Exception as ex:
                    logger.error(
                        f"Failed to update schema or entry: {ex}", exc_info=True)
            else:
                logger.error(
                    f"Error toggling favorite status: {e}", exc_info=True)

    def update_app_details(self, app_id, name, version, exe_path):
        """Updates basic application details and converts exe_path to relative."""
        rel_exe_path = PathManager.to_relative_path(exe_path)
        query = "UPDATE apps SET name = ?, current_version = ?, exe_path = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, version, rel_exe_path, app_id))
                conn.commit()
                logger.info(
                    f"App {app_id} updated: {name}, v{version}, {rel_exe_path}")
                return True
        except Exception as e:
            logger.error(f"Error updating app details for ID {app_id}: {e}")
            return False
