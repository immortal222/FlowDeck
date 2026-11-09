# Standard Library Imports
import logging
import os
import sqlite3
from urllib.parse import quote_plus

# Third-Party Library Imports


# Local Module Imports
from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class ScoopAPI:
    """Handles communication with Scoop repositories via GitHub raw content and local catalog DB."""

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
        """
        Searches for an application in Scoop buckets.
        Accepts either a string or a list of candidate names.
        Returns metadata dictionary or None.
        """
        import requests  # Staying here for fast startup, as requests is only used in this method

        # Normalize input parameter into a candidates list at the very beginning
        if isinstance(app_name, list):
            candidates = [c for c in app_name if c]
        elif isinstance(app_name, str) and app_name.strip():
            candidates = [app_name.strip()]
        else:
            candidates = []

        if not candidates:
            return None

        # Primary candidate used for live online bucket search
        primary_name = candidates[0]
        app_name_lower = primary_name.lower().strip()

        # Normalize names for Scoop compatibility
        app_name_lower = app_name_lower.replace("+", "plus").replace(" ", "-")

        # Phase A: Online Bucket Lookup via GitHub
        slugs = []
        base_name = candidates[0].lower().strip().replace("+", "plus")

        # 1. Standard slug (replace spaces and underscores with hyphens)
        slugs.append(base_name.replace(" ", "-").replace("_", "-"))

        # 2. Clean slug (remove hyphens, underscores, and spaces)
        slugs.append(base_name.replace(
            "-", "").replace("_", "").replace(" ", ""))

        # 3. Strip common noise words
        noise_words = [
            "portable", "community", "edition", "desktop",
            "free", "installer", "setup", "win32", "win64", "x64", "x86"
        ]
        clean_words_str = base_name
        for word in noise_words:
            clean_words_str = clean_words_str.replace(word, "")

        clean_words_str = clean_words_str.strip("-_ ")
        if clean_words_str:
            slugs.append(clean_words_str.replace(" ", "-").replace("_", "-"))
            slugs.append(clean_words_str.replace(
                "-", "").replace("_", "").replace(" ", ""))

        print(slugs)

        # Deduplicate while preserving order
        unique_slugs = []
        for s in slugs:
            if s and s not in unique_slugs:
                unique_slugs.append(s)

        for slug in unique_slugs:
            for bucket_name, url_template in self.buckets.items():
                url = url_template.format(slug)
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(
                            f"Found {primary_name} (slug: '{slug}') in bucket '{bucket_name}'."
                        )

                        # Determine homepage URL or fallback to Google Search link
                        homepage = data.get("homepage", "")
                        if isinstance(homepage, list) and homepage:
                            homepage = homepage[0]
                        if not homepage:
                            homepage = f"https://www.google.com/search?q={quote_plus(primary_name)}"

                        return {
                            "name": data.get("name", primary_name),
                            "version": data.get("version", "1.0"),
                            "description": data.get("description", ""),
                            "url": data.get("url"),
                            "source": "scoop",
                            "bucket": bucket_name,
                            "homepage": homepage,
                            "architecture": data.get("architecture"),
                            "bin": data.get("bin")
                        }
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    logger.error(
                        f"Server is down or unreachable for Scoop ({primary_name} / {slug}): {e}"
                    )
                    return "SERVER_ERROR"
                except requests.RequestException as e:
                    logger.error(
                        f"Network error while searching for {primary_name} ({slug}): {e}"
                    )

        # Phase B: Local catalog database lookup (multi-stage fallback)
        # Combine original candidates with unique_slugs from Phase A
        db_search_terms = []
        for cand in candidates:
            if cand and cand not in db_search_terms:
                db_search_terms.append(cand)
        for slug in unique_slugs:
            if slug and slug not in db_search_terms:
                db_search_terms.append(slug)

        print(f"\n--- [SCOOP DEBUG] ---")
        print(f"--> Incoming DB Candidates: {db_search_terms}")

        if os.path.exists(self.catalog_db) and db_search_terms:
            try:
                conn = sqlite3.connect(self.catalog_db)
                cursor = conn.cursor()
                result = None

                # Stage 1: Exact query matching for each search term across user_friendly_name and scoop_id
                for cand in db_search_terms:
                    search_term = cand.strip()
                    cursor.execute("""
                        SELECT scoop_id, bucket FROM apps 
                        WHERE user_friendly_name LIKE ? OR scoop_id LIKE ?
                        LIMIT 1
                    """, (search_term, search_term))

                    result = cursor.fetchone()
                    if result:
                        print(
                            f"--> DB Match found at Stage 1 for term '{search_term}': {result}")
                        break

                # Stage 2: Fallback prefix search using the primary candidate name
                if not result and len(candidates) > 0:
                    root_term = candidates[0].strip() + "%"
                    print(
                        f"--> Attempting Stage 2 prefix search with: '{root_term}'")
                    cursor.execute("""
                        SELECT scoop_id, bucket FROM apps 
                        WHERE user_friendly_name LIKE ? OR scoop_id LIKE ?
                        ORDER BY LENGTH(user_friendly_name) ASC
                        LIMIT 1
                    """, (root_term, root_term))

                    result = cursor.fetchone()
                    if result:
                        print(
                            f"--> DB Match found at Stage 2 for prefix '{root_term}': {result}")

                conn.close()
                print(f"---------------------\n")

                if result:
                    db_scoop_id, db_bucket = result[0], result[1]
                    logger.info(
                        f"[CATALOG] Successful mapping for '{primary_name}' -> ID: '{db_scoop_id}' in bucket '{db_bucket}'.")

                    # Fetch live data using the mapped ID
                    url = self.buckets[db_bucket].format(db_scoop_id)
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        data = response.json()

                        # Determine homepage URL or fallback to Google Search link
                        homepage = data.get("homepage", "")
                        if isinstance(homepage, list) and homepage:
                            homepage = homepage[0]
                        if not homepage:
                            homepage = f"https://www.google.com/search?q={quote_plus(primary_name)}"

                        return {
                            "name": data.get("name", primary_name),
                            "version": data.get("version", "1.0"),
                            "description": data.get("description", ""),
                            "url": data.get("url"),
                            "source": "scoop",
                            "bucket": db_bucket,
                            "homepage": homepage,
                            "architecture": data.get("architecture"),
                            "bin": data.get("bin")
                        }
            except Exception as e:
                logger.error(f"Error querying scoop_catalog.db: {e}")

        logger.warning(f"Application '{primary_name}' not found in Scoop.")
        return None
