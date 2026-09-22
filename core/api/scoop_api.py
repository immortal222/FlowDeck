import logging
import os
import sqlite3

import requests

from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class ScoopAPI:
    """Handles communication with Scoop repositories via GitHub raw content."""

    def __init__(self):
        # Base URLs for Scoop bucket JSON manifests
        self.buckets = {
            "main": "https://raw.githubusercontent.com/ScoopInstaller/Main/master/bucket/{}.json",
            "extras": "https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/{}.json"
        }
        self.catalog_db = PathManager.get_resource_path("scoop_catalog.db")
        print(
            f"[ScoopAPI] Initialized with catalog database at: {self.catalog_db}")

    def search_app(self, app_name):
        """Searches for an application in Scoop buckets. Returns metadata dictionary or None."""
        app_name_lower = app_name.lower().strip()

        # Normalize names for Scoop compatibility
        app_name_lower = app_name_lower.replace("+", "plus").replace(" ", "-")

        for bucket_name, url_template in self.buckets.items():
            url = url_template.format(app_name_lower)
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Found {app_name} in bucket '{bucket_name}'.")

                    return {
                        "name": data.get("name", app_name),
                        "version": data.get("version", "1.0"),
                        "description": data.get("description", ""),
                        "url": data.get("url"),
                        "source": "scoop",
                        "bucket": bucket_name,
                        "homepage": data.get("homepage", ""),
                        "architecture": data.get("architecture"),
                        "bin": data.get("bin")
                    }
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.error(
                    f"Server is down or unreachable for Scoop ({app_name}): {e}")
                return "SERVER_ERROR"
            except requests.RequestException as e:
                logger.error(
                    f"Network error while searching for {app_name}: {e}")

        # Phase B: Local catalog database lookup (fallback)
        search_term = app_name.strip()

        print(f"\n--- [SCOOP DEBUG] ---")
        print(f"--> Incoming App Name: '{app_name}'")
        print(f"--> Search Term for DB Query: '{search_term}'")

        if os.path.exists(self.catalog_db):
            try:
                conn = sqlite3.connect(self.catalog_db)
                cursor = conn.cursor()

                # Simple case-insensitive query using LIKE
                cursor.execute("""
                    SELECT scoop_id, bucket FROM apps 
                    WHERE user_friendly_name LIKE ? OR scoop_id LIKE ?
                    LIMIT 1
                """, (search_term, search_term))

                result = cursor.fetchone()
                conn.close()

                print(f"--> DB Query Result: {result}")
                print(f"---------------------\n")

                if result:
                    db_scoop_id, db_bucket = result[0], result[1]
                    logger.info(
                        f"[CATALOG] Successful mapping for '{app_name}' -> ID: '{db_scoop_id}' in bucket '{db_bucket}'.")

                    # Fetch live data using the mapped ID
                    url = self.buckets[db_bucket].format(db_scoop_id)
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "name": data.get("name", app_name),
                            "version": data.get("version", "1.0"),
                            "description": data.get("description", ""),
                            "url": data.get("url"),
                            "source": "scoop",
                            "bucket": db_bucket,
                            "homepage": data.get("homepage", ""),
                            "architecture": data.get("architecture"),
                            "bin": data.get("bin")
                        }
            except Exception as e:
                logger.error(f"Error querying scoop_catalog.db: {e}")

        logger.warning(f"Application {app_name} not found in Scoop.")
        return None
