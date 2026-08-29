# Standard Library Imports
import configparser
import logging
import os
import re
import shutil
import socket

# Third-Party Library Imports
import pefile

# Local Module Imports
from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


def is_internet_available():
    """Verifies active internet connectivity via DNS connection attempt."""
    try:
        # Connection attempt to Cloudflare DNS
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False


def get_folder_size_gb(folder_path):
    """Calculates total directory size in Gigabytes."""
    if not folder_path or not os.path.exists(folder_path):
        return 0.0
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024**3)


def _normalize_version_string(value):
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text or text in {"", "none", "unknown", "n/a", "-"}:
        return None
    return text.lstrip('v')


def _version_parts(value):
    value = _normalize_version_string(value)
    if value is None:
        return None

    parts = []
    for part in value.split('.'):
        if part.isdigit():
            parts.append(int(part))
        else:
            # preserve non-numeric suffixes by ignoring them for comparison
            break

    # Normalize trailing zeros so 3.70.6.0 == 3.70.6
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()

    return parts


def is_update_available(current_ver, latest_ver):
    """Compares version strings and returns True if an update is available."""
    latest_norm = _normalize_version_string(latest_ver)
    if latest_norm is None:
        return False

    current_parts = _version_parts(current_ver)
    latest_parts = _version_parts(latest_ver)

    if current_parts is not None and latest_parts is not None:
        return latest_parts > current_parts

    # Fallback to simple string comparison when numeric parsing fails
    c = _normalize_version_string(current_ver) or ""
    l = latest_norm
    return l > c


def get_disk_stats(path):
    """Retrieves disk usage statistics for a specific directory path."""
    if not os.path.exists(path):
        path = os.path.dirname(path) if os.path.dirname(path) else "."

    usage = shutil.disk_usage(path)
    total_gb = usage.total / (1024**3)
    used_gb = usage.used / (1024**3)
    free_gb = usage.free / (1024**3)
    percent_used = (usage.used / usage.total) * 100
    return {
        'total_gb': total_gb,
        'used_gb': used_gb,
        'free_gb': free_gb,
        'percent_used': int(percent_used)
    }


def get_portable_apps_metadata(app_folder):
    """
    Parses appinfo.ini for PortableApps.com compliant applications.
    Returns a dictionary with metadata or None if parsing fails.
    """
    logger.debug(f"Searching for appinfo.ini at path: {app_folder}")
    ini_path = os.path.join(app_folder, "App", "AppInfo", "appinfo.ini")

    if not os.path.exists(ini_path):
        logger.debug("File NOT found at path.")
        return None

    try:
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8-sig')

        name = None
        version = None
        start_exe = None

        if config.has_section('Details'):
            name = config.get('Details', 'name', fallback=None)
            if name:
                name = name.replace(", Portable Edition",
                                    "").replace(" Portable", "")

        if config.has_section('Version'):
            version = config.get('Version', 'displayversion', fallback=None)

        if config.has_section('Control'):
            start_exe = config.get('Control', 'start', fallback=None)

        if name or version:
            logger.debug(
                f"Found metadata in appinfo.ini - Name: {name}, Version: {version}, EXE: {start_exe}")
            return {
                'name': name,
                'version': version,
                'start_exe': start_exe
            }
        else:
            logger.debug(
                f"Insufficient metadata found. Sections: {config.sections()}")
    except Exception as e:
        logger.error(f"Error reading {ini_path}: {e}")

    return None


def scan_ini_files(root_folder):
    """
    Scans a PortableApps root for appinfo.ini files and returns a list of found metadata.
    """
    if not root_folder or not os.path.isdir(root_folder):
        return []

    try:
        ini_files = []
        for dirpath, _, filenames in os.walk(root_folder):
            if "appinfo.ini" in filenames:
                ini_files.append(os.path.join(dirpath, "appinfo.ini"))
        return ini_files
    except Exception as e:
        logger.error(f"Error scanning ini files in {root_folder}: {e}")
        return []


def update_all_ini_files(root_folder, db):
    """
    Updates the database using the metadata 
    found in all appinfo.ini files.
    Returns a list of updated app records.
    """

    ini_files = []
    ini_files = scan_ini_files(root_folder)

    updated_apps = []
    for ini_path in sorted(ini_files):
        app_folder = os.path.dirname(
            os.path.dirname(os.path.dirname(ini_path)))
        metadata = get_portable_apps_metadata(app_folder)
        if not metadata:
            continue

        app_name = metadata.get("name")
        if not app_name:
            continue

        version = metadata.get("version") or "1.0"
        start_exe = metadata.get("start_exe")
        exe_path = None

        if start_exe:
            relative_exe_path = os.path.join(app_folder, start_exe)
            exe_path = os.path.abspath(relative_exe_path)
        else:
            for candidate in [os.path.join(app_folder, "App"), app_folder]:
                if os.path.isdir(candidate):
                    for root, _, files in os.walk(candidate):
                        for filename in files:
                            if filename.lower().endswith(".exe"):
                                exe_path = os.path.abspath(
                                    os.path.join(root, filename))
                                break
                        if exe_path:
                            break
                if exe_path:
                    break

        if not exe_path:
            exe_path = os.path.abspath(app_folder)

        if db and hasattr(db, "add_or_update_app"):
            db.add_or_update_app(
                name=app_name,
                local_path=app_folder,
                exe_path=exe_path,
                current_version=version,
            )

        updated_apps.append({
            "name": app_name,
            "folder": PathManager.to_absolute_path(app_folder),
            "version": version,
            "start_exe": start_exe,
            "exe_path": PathManager.to_absolute_path(exe_path),
        })
    return updated_apps


def get_clean_app_name(name):
    """
    Sanitizes application names, preserving specific symbols like '++'.
    Retains alphanumeric characters, spaces, and hyphens.
    """
    if not name:
        return ""

    # Special case for Notepad++ (ignores spaces and case during check)
    if "notepad++" in name.lower().replace(" ", ""):
        return "Notepad++"

    # Keep only alphanumeric characters, spaces, hyphens, and underscores
    cleaned = "".join([c for c in name if c.isalnum()
                      or c.isspace() or c in ('-', '_')])
    return " ".join(cleaned.split()).title()


def get_normalized_app_name(name):
    """Normalizes common PE/folder name variants into a display-friendly app name."""
    if not name:
        return ""

    text = str(name)
    for token in [
        "_portable", "-portable", ".portable", " portable", " Application",
        " application", " applications", " app", " installer", " install",
        " setup", "x64", "x86", "64bit", "32bit", " beta", " preview",
        " release"
    ]:
        text = text.replace(token, "")

    text = text.replace("notepad ++", "Notepad++")
    return get_clean_app_name(text)


def get_safe_folder_path(base_dir, desired_name, current_path=None):
    """
    Generates a system-safe directory path based on application name.
    Handles naming conflicts by appending numeric suffixes.
    """
    abs_base_dir = PathManager.to_absolute_path(base_dir)
    safe_folder_name = re.sub(r'[\\/*?:"<>|]', "", desired_name).strip()
    new_dir_path = os.path.join(
        abs_base_dir, safe_folder_name).replace("\\", "/")

    counter = 2
    base_new_dir_path = new_dir_path

    while os.path.exists(new_dir_path):
        if current_path and new_dir_path.lower() == current_path.lower():
            break
        elif not current_path:
            break

        new_dir_path = f"{base_new_dir_path} {counter}"
        counter += 1

    return new_dir_path


def get_resource_path(relative_path):
    """
    Resolves resource paths for both development and bundled environments.
    """
    return PathManager.get_resource_path(relative_path)


def find_app_executables(folder_path):
    """
    Crawls directory for executables, excluding common setup and system utilities.
    """
    executables = []
    excluded_terms = ['unins', 'setup', 'install', 'helper',
                      '7za.exe', 'crashpad', 'notification_helper']

    if not os.path.exists(folder_path):
        return executables

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".exe"):
                if any(term in file.lower() for term in excluded_terms):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                executables.append(rel_path.replace("\\", "/"))

    return sorted(executables, key=lambda x: (x.count('/'), x.lower()))


def get_pe_version(exe_path):
    """Extracts internal version from the PE executable safely and quickly."""
    try:
        with pefile.PE(exe_path) as pe:
            if hasattr(pe, 'VS_FIXEDFILEINFO') and pe.VS_FIXEDFILEINFO:
                fi = pe.VS_FIXEDFILEINFO[0]
                ms = fi.FileVersionMS
                ls = fi.FileVersionLS
                return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    except ImportError:
        logger.warning("Module 'pefile' missing. Run: pip install pefile")
    except Exception:
        pass
    return None


def get_pe_name(file_path):
    try:
        pe = pefile.PE(file_path)
        if not hasattr(pe, 'FileInfo'):
            logger.warning("No version info found")

        # Iterate through the parsed FileInfo structures
        for file_info in pe.FileInfo:
            for info_block in file_info:
                # Look specifically for StringTable objects
                if hasattr(info_block, 'StringTable'):
                    for entry in info_block.StringTable:
                        # Look for the 'ProductName' or 'FileDescription' keys
                        for key, value in entry.entries.items():
                            key_str = key.decode('utf-8', errors='ignore')
                            if key_str == 'ProductName':
                                return get_normalized_app_name(value.decode('utf-8', errors='ignore'))
    except Exception as e:
        logger.error(f"Error loading file: {e}")
    finally:
        pe.close()
    return None
