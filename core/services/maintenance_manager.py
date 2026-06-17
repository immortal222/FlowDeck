

import os
import re
import sqlite3

from datetime import datetime

from core.api.scoop_api import ScoopAPI
from core.utils import get_portable_apps_metadata, get_safe_folder_path


class MaintenanceManager:
    """ This file includes the automatic maintenance engine, orphan record detection, and new folder scanning. """

    def __init__(self, db_manager, config_dict):
        self.db = db_manager
        self.config = config_dict
        # --- ΝΕΟ: 2. Αρχικοποίηση του ScoopAPI ---
        self.scoop = ScoopAPI()

    def _detect_db_schema(self, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        table_name = 'apps' if 'apps' in tables else (
            'applications' if 'applications' in tables else None)
        if not table_name:
            return None, []

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return table_name, columns

    def extract_name_and_version(self, folder_name):
        """Extracts application name and version from a folder name string."""
        clean_name = folder_name.replace("_portable", "").replace(
            "-portable", "").replace(".portable", "")
        version_pattern = r'[-_]v?(\d+\.\d+(?:\.\d+)?(?:[-_][a-zA-Z0-9]+)?)'
        match = re.search(version_pattern, clean_name)

        if match:
            version = match.group(1)
            name_part = clean_name[:match.start()]
            name = name_part.replace("-", " ").replace("_", " ").strip()
            return name, version

        name = clean_name.replace("-", " ").replace("_", " ").strip()
        return name, "1.0.0"

    def find_main_executable(self, folder_path):
        """Scans a folder to find the most likely main executable using a scoring system."""
        exclude_names = {
            "uninstall.exe", "uninst.exe", "setup.exe", "install.exe",
            "updater.exe", "update.exe", "crashreporter.exe",
            "helper.exe", "vc_redist.exe", "dxsetup.exe", "config.exe",
            "dependencies.exe", "unins000.exe", "unins001.exe", "elevate.exe"
        }

        candidates = []
        folder_name_lower = os.path.basename(folder_path).lower()

        try:
            for entry in os.scandir(folder_path):
                if entry.is_file() and entry.name.lower().endswith(".exe"):
                    if entry.name.lower() not in exclude_names:
                        candidates.append(
                            (entry.path, entry.name, os.path.getsize(entry.path), True))
        except Exception:
            pass

        if not candidates:
            try:
                for root, dirs, files in os.walk(folder_path):
                    depth = root[len(folder_path):].count(os.sep)
                    if depth > 2:
                        continue
                    for file in files:
                        if file.lower().endswith(".exe") and file.lower() not in exclude_names:
                            full_path = os.path.join(root, file)
                            candidates.append(
                                (full_path, file, os.path.getsize(full_path), False))
            except Exception:
                pass

        if not candidates:
            return None

        best_cand = None
        best_score = -1

        for path, name, size, is_root in candidates:
            name_no_ext = os.path.splitext(name)[0].lower()
            score = 0
            if name_no_ext in folder_name_lower or folder_name_lower in name_no_ext:
                score += 50
            if is_root:
                score += 30
            size_mb = size / (1024 * 1024)
            score += min(20, int(size_mb))

            if score > best_score:
                best_score = score
                best_cand = path
        return best_cand

    def execute_scan_and_repair(self, dialog_callback=None):
        """
        Performs the main maintenance task:
        Phase A: Cleanup orphaned records (folders/files no longer existing).
        Phase B: Scan for new portable folders and register them.
        """
        if hasattr(self.db, 'db_path') and self.db.db_path:
            db_path = self.db.db_path
        else:
            root_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), ".."))
            db_path = os.path.join(root_dir, "linkweave.db")
            if not os.path.exists(db_path):
                return False, 0, 0, f"Database file not found."

        self.db.create_backup()
        removed_count = 0
        added_count = 0

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            table_name, columns = self._detect_db_schema(cursor)
            if not table_name:
                return False, 0, 0, "Could not detect DB schema table."

            dir_col = 'local_path' if 'local_path' in columns else None
            exe_col = 'exe_path' if 'exe_path' in columns else None
            if not dir_col or not exe_col:
                return False, 0, 0, f"Required columns missing."

            # --- PHASE A: REPAIR (ORPHAN CLEANUP) ---
            cursor.execute(
                f"SELECT id, name, {dir_col}, {exe_col} FROM {table_name}")
            registered_apps = cursor.fetchall()

            registered_dirs = set()
            for app_id, app_name, install_dir, exe_path in registered_apps:
                norm_dir = os.path.abspath(install_dir).replace(
                    "\\", "/") if install_dir else ""
                registered_dirs.add(norm_dir.lower())
                if not install_dir or not os.path.exists(install_dir) or (exe_path and not os.path.exists(exe_path)):
                    cursor.execute(
                        f"DELETE FROM {table_name} WHERE id = ?", (app_id,))
                    removed_count += 1

            # --- PHASE B: SCAN (AUTO DETECTION & FOLDER RENAMING) ---
            install_path = self.config.get("install_path", "")
            if install_path and os.path.isdir(install_path):
                for entry in os.scandir(install_path):
                    if entry.is_dir():
                        norm_entry_path = os.path.abspath(
                            entry.path).replace("\\", "/")
                        if norm_entry_path.lower() not in registered_dirs:
                            main_exe = self.find_main_executable(entry.path)

                            if main_exe:
                                main_exe_norm = os.path.abspath(
                                    main_exe).replace("\\", "/")

                                # 1. Try to find metadata from appinfo.ini (PortableApps.com)
                                metadata = get_portable_apps_metadata(
                                    entry.path)
                                is_paf = False
                                if metadata:
                                    is_paf = True
                                    guessed_name = metadata.get(
                                        'name') or entry.name
                                    guessed_version = metadata.get(
                                        'version') or "1.0.0"
                                else:
                                    # 2. Fallback to extracting from folder name
                                    guessed_name, guessed_version = self.extract_name_and_version(
                                        entry.name)

                                while True:
                                    final_name = guessed_name
                                    final_version = guessed_version

                                    if dialog_callback:
                                        approved, user_name, user_version = dialog_callback(
                                            entry.name, guessed_name, guessed_version)
                                        if not approved:
                                            break
                                        final_name = user_name
                                        final_version = user_version

                                    # 3. Search for metadata in Scoop API
                                    is_scoop = False
                                    scoop_id = None
                                    scoop_data = self.scoop.search_app(
                                        final_name)

                                    if scoop_data and isinstance(scoop_data, dict):
                                        is_scoop = True
                                        scoop_id = final_name.lower().strip().replace(" ", "-")

                                    # --- PHYSICAL FOLDER RENAMING ---
                                    actual_dir_path = norm_entry_path
                                    actual_exe_path = main_exe_norm

                                    # If not a PAF app (ZIP/7Z), rename folder to match app name
                                    if not is_paf:
                                        base_directory = os.path.dirname(
                                            norm_entry_path)
                                        new_dir_path = get_safe_folder_path(
                                            base_directory, final_name, norm_entry_path)

                                        # Προσπάθεια μετονομασίας αν το νέο όνομα είναι διαφορετικό
                                        if new_dir_path.lower() != norm_entry_path.lower():
                                            try:
                                                os.rename(
                                                    norm_entry_path, new_dir_path)
                                                actual_dir_path = new_dir_path

                                                relative_exe = main_exe_norm[len(
                                                    norm_entry_path):].lstrip("/")
                                                actual_exe_path = os.path.join(
                                                    actual_dir_path, relative_exe).replace("\\", "/")

                                                norm_entry_path = actual_dir_path
                                                main_exe_norm = actual_exe_path
                                            except Exception as e:
                                                print(
                                                    f"⚠️ Αποτυχία μετονομασίας φακέλου: {e}")
                                                actual_dir_path = norm_entry_path
                                                actual_exe_path = main_exe_norm

                                    # --- DATABASE REGISTRATION ---
                                    insert_data = {}
                                    if 'name' in columns:
                                        insert_data['name'] = final_name
                                    if dir_col in columns:
                                        insert_data[dir_col] = actual_dir_path
                                    if exe_col in columns:
                                        insert_data[exe_col] = actual_exe_path

                                    if 'source' in columns:
                                        insert_data['source'] = 'scoop' if is_scoop else 'manual'

                                    if is_scoop:
                                        if 'scoop_id' in columns:
                                            insert_data['scoop_id'] = scoop_id
                                        elif 'app_id' in columns:
                                            insert_data['app_id'] = scoop_id

                                    if 'current_version' in columns:
                                        insert_data['current_version'] = final_version
                                    elif 'version' in columns:
                                        insert_data['version'] = final_version
                                    if 'is_favorite' in columns:
                                        insert_data['is_favorite'] = 0
                                    elif 'favorite' in columns:
                                        insert_data['favorite'] = 0
                                    if 'latest_version' in columns:
                                        insert_data['latest_version'] = scoop_data.get(
                                            "version") if is_scoop else None

                                    keys = list(insert_data.keys())
                                    values = list(insert_data.values())
                                    placeholders = ", ".join(["?"] * len(keys))
                                    insert_sql = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({placeholders})"

                                    try:
                                        cursor.execute(insert_sql, values)
                                        added_count += 1
                                        # Add new path to registered list to avoid duplicates in the same scan
                                        registered_dirs.add(
                                            actual_dir_path.lower())
                                        break
                                    except sqlite3.IntegrityError as e:
                                        if "UNIQUE" in str(e).upper() or "NAME" in str(e).upper():
                                            print(
                                                f"⚠️ Το όνομα '{final_name}' υπάρχει ήδη! Επιστροφή στο UI.")
                                            guessed_name = f"{final_name} 2"
                                            guessed_version = final_version
                                            if dialog_callback:
                                                continue
                                            else:
                                                insert_data['name'] = f"{final_name} ({datetime.now().strftime('%H%M%S')})"
                                                cursor.execute(insert_sql, list(
                                                    insert_data.values()))
                                                added_count += 1
                                                break
                                        else:
                                            raise e

            conn.commit()
            conn.close()
            return True, removed_count, added_count, None

        except Exception as e:
            return False, 0, 0, str(e)
