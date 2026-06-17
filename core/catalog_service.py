import logging
import os
import sqlite3

from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class CatalogService:
    """Handles application mapping between friendly names and Scoop IDs using a local database."""

    def __init__(self):
        self.db_path = PathManager.get_resource_path("scoop_catalog.db")

    def get_scoop_id_by_name(self, app_name):
        """Searches for a scoop_id in the catalog using the user_friendly_name column."""
        if not os.path.exists(self.db_path):
            logger.warning("Scoop catalog database not found.")
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "SELECT scoop_id FROM apps WHERE user_friendly_name LIKE ? OR user_friendly_name = ? LIMIT 1"
                cursor.execute(query, (f"%{app_name}%", app_name.strip()))

                row = cursor.fetchone()
                if row:
                    return row[0]
        except Exception as e:
            logger.error(f"Error mapping name to scoop_id: {e}")

        return None
