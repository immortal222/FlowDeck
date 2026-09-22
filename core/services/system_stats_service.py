# Standard Library Imports
import logging
import os
import sqlite3

# Local Module Imports
from core.services.path_manager import PathManager
from core.utils import get_folder_size_gb, is_update_available
from locales.localization import _

logger = logging.getLogger(__name__)


class SystemStatsService:
    """Service for gathering system, database, and usage statistics for FlowDeck."""

    def __init__(self, db_manager, config_manager):
        self.db = db_manager
        self.config = config_manager

    def get_all_stats(self):
        """Fetches and returns a complete dictionary of system stats."""
        stats = {}

        # 1. Basic numbers for applications and favorites
        stats['installed_apps'] = self._get_installed_apps_count()
        stats['need_updates'] = self._get_updates_count()
        stats['favorites'] = self._get_favorites_count()

        # 2. Total Apps folder size
        stats['apps_folder_size'] = self._get_apps_folder_size()

        # 3. Database integrity check
        stats['db_status'] = self._check_database_integrity()

        # 4. Scoop catalog version / last check date
        stats['scoop_version'] = self._get_scoop_catalog_version()

        # 5. Top 5 most launched applications
        stats['most_launched'] = self._get_top_launched_apps(limit=5)

        # 6. Top 5 largest applications by disk space
        stats['largest_apps'] = self._get_top_sized_apps(limit=5)

        return stats

    def _get_installed_apps_count(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM apps")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting installed apps: {e}")
            return 0

    def _get_updates_count(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT current_version, latest_version FROM apps WHERE latest_version IS NOT NULL AND latest_version != ''"
                )
                rows = cursor.fetchall()
                pending = 0
                for current_ver, latest_ver in rows:
                    if is_update_available(current_ver, latest_ver):
                        pending += 1
                return pending
        except Exception as e:
            logger.error(f"Error counting pending updates: {e}")
            return 0

    def _get_favorites_count(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM apps WHERE is_favorite = 1")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting favorites: {e}")
            return 0

    def _get_apps_folder_size(self):
        install_path = self.config.get("install_path", "")
        abs_path = PathManager.to_absolute_path(install_path)
        if abs_path and os.path.exists(abs_path):
            size_gb = get_folder_size_gb(abs_path)
            if size_gb >= 1.0:
                return f"{size_gb:.2f} GB"
            else:
                size_mb = size_gb * 1024
                return f"{size_mb:.1f} MB"
        return "0 MB"

    def _check_database_integrity(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                if result and result[0] == "ok":
                    return _("set_db_status_ok", "OK")
                return _("set_db_status_maintenance", "Needs Maintenance")
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")
            return _("set_db_status_maintenance", "Needs Maintenance")

    def _get_scoop_catalog_version(self):
        try:
            scoop_db_path = PathManager.get_resource_path("scoop_catalog.db")
            if os.path.exists(scoop_db_path):
                with sqlite3.connect(scoop_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT version FROM metadata ORDER BY updated_at DESC LIMIT 1")
                    row = cursor.fetchone()
                    if row and row[0]:
                        return str(row[0])
        except Exception as e:
            logger.error(f"Error reading scoop catalog version: {e}")

        # Fallback to config if database check fails or file does not exist
        last_check = self.config.get("last_scoop_update", None)
        if last_check:
            return str(last_check)
        return "N/A"

    def _get_top_launched_apps(self, limit=5):
        """Returns the top launched applications ordered by launch count."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, usage_count FROM apps ORDER BY usage_count DESC LIMIT ?", (
                        limit,)
                )
                rows = cursor.fetchall()
                results = [
                    f"{row[0]} ({row[1]})" for row in rows if row[1] > 0]
                while len(results) < limit:
                    results.append("-")
                return results
        except Exception as e:
            logger.error(f"Error getting top launched apps: {e}")
            return ["-"] * limit

    def _get_top_sized_apps(self, limit=5):
        """Calculates and returns the largest application folders in the portable root."""
        try:
            install_path = self.config.get("install_path", "")
            abs_root = PathManager.to_absolute_path(install_path)
            if not abs_root or not os.path.exists(abs_root):
                return ["-"] * limit

            app_sizes = []
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, local_path FROM apps")
                apps = cursor.fetchall()

            for name, rel_path in apps:
                full_path = PathManager.to_absolute_path(rel_path)
                if full_path and os.path.exists(full_path):
                    folder_path = os.path.dirname(
                        full_path) if os.path.isfile(full_path) else full_path
                    size_gb = get_folder_size_gb(folder_path)
                    app_sizes.append((name, size_gb))

            # Sort descending by size
            app_sizes.sort(key=lambda x: x[1], reverse=True)

            results = []
            for name, size_gb in app_sizes[:limit]:
                if size_gb >= 1.0:
                    formatted_size = f"{size_gb:.2f} GB"
                else:
                    formatted_size = f"{size_gb * 1024:.1f} MB"
                results.append(f"{name} ({formatted_size})")

            while len(results) < limit:
                results.append("-")
            return results
        except Exception as e:
            logger.error(f"Error calculating largest app folders: {e}")
            return ["-"] * limit
