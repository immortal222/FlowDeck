import logging
import os
import shutil
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import QMessageBox

from core.services.path_manager import PathManager
from locales.localization import _

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connection, schema creation, and CRUD operations."""

    def __init__(self, db_name="flowdeck.db"):
        # Initialize database path and ensure connection
        self.db_path = PathManager.get_database_path(db_name)

        # 1. Handle missing database file
        if not os.path.exists(self.db_path):
            if self.has_backups():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle(_("db_restore_title", "Επαναφορά Βάσης"))
                msg.setText(
                    _("db_restore_prompt", "Η βάση δεδομένων δεν βρέθηκε, αλλά εντοπίστηκε αντίγραφο ασφαλείας.\n\nΘέλετε να γίνει επαναφορά από το πιο πρόσφατο backup;"))
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)

                if msg.exec_() == QMessageBox.Yes:
                    self.restore_from_latest_backup()

        # 2. Handle corrupted database file
        elif self.is_corrupted():
            logger.error(
                "Database file is corrupted. Starting automatic restoration...")
            self.restore_from_latest_backup()

        self.create_tables()

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
        backups_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        if os.path.exists(backups_dir):
            backups = [f for f in os.listdir(backups_dir) if f.endswith(".db")]
            return len(backups) > 0
        return False

    def create_backup(self):
        """Creates a timestamped backup and triggers old backup cleanup."""
        backups_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        os.makedirs(backups_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dest = os.path.join(
            backups_dir, f"flowdeck_backup_{timestamp}.db")

        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_dest)
                logger.info(f"Backup created: {backup_dest}")
                self._cleanup_old_backups(backups_dir)
                return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
        return False

    def _cleanup_old_backups(self, backups_dir):
        """Retains only the 5 most recent backup files."""
        try:
            backups = sorted([f for f in os.listdir(
                backups_dir) if f.endswith(".db")])

            while len(backups) > 5:
                oldest = backups.pop(0)
                os.remove(os.path.join(backups_dir, oldest))
                logger.info(f"Removed old backup: {oldest}")
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")

    def restore_from_latest_backup(self):
        """Restores the database from the most recent backup file."""
        backups_dir = os.path.join(os.path.dirname(self.db_path), "backups")

        if not os.path.exists(backups_dir):
            logger.warning("Backup directory not found.")
            return False

        backups = [f for f in os.listdir(backups_dir) if f.endswith(".db")]
        if not backups:
            logger.warning("No backups available in the directory.")
            return False

        latest_backup = sorted(backups)[-1]
        backup_full_path = os.path.join(backups_dir, latest_backup)

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
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

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
        """Inserts or updates an application entry based on its unique name."""
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
                cursor.execute(query, (name, local_path, exe_path,
                               source, update_url, current_version, latest_version, homepage))
                conn.commit()
                return True
        except Exception as e:
            print(
                f"\n❌ [DATABASE ERROR] Failed to write {name} to the database!")
            print(f"Error details: {e}\n")

            logger.error(
                f"Error while adding application {name}: {e}", exc_info=True)
            return False

    def get_all_apps(self):
        """Retrieves all applications sorted by name."""
        query = "SELECT * FROM apps ORDER BY name COLLATE NOCASE ASC"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Σφάλμα κατά την ανάκτηση εφαρμογών: {e}")
            return []

    def get_app_by_name(self, name):
        """Retrieves metadata for a specific application by name."""
        query = "SELECT * FROM apps WHERE name = ?"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                row = cursor.fetchone()
                return dict(row) if row else None
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
                print(
                    f"[DB] Success: is_favorite for ID {app_id} changed to {status}")

        except Exception as e:
            error_msg = str(e).lower()
            if "no such column: is_favorite" in error_msg or "has no column" in error_msg:
                print(
                    "[DB] Column 'is_favorite' missing. Adding it automatically...")
                try:
                    with self.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "ALTER TABLE apps ADD COLUMN is_favorite INTEGER DEFAULT 0")
                        cursor.execute(
                            "UPDATE apps SET is_favorite = ? WHERE id = ?", (status, app_id))
                        conn.commit()
                        print(
                            f"[DB] Success after schema update: is_favorite changed to {status}")
                except Exception as ex:
                    print(f"[DB ERROR] Failed to update schema or entry: {ex}")
            else:
                print(f"[DB ERROR] Error toggling favorite status: {e}")

    def update_app_details(self, app_id, name, version, exe_path):
        """Updates basic application details for repair or edit purposes."""
        query = "UPDATE apps SET name = ?, current_version = ?, exe_path = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, version, exe_path, app_id))
                conn.commit()
                logger.info(
                    f"App {app_id} updated: {name}, v{version}, {exe_path}")
                return True
        except Exception as e:
            logger.error(f"Error updating app details for ID {app_id}: {e}")
            return False
