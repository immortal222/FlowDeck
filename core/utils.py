# Standard Library Imports
import configparser
import logging
import os
import re
import shutil
import socket
import subprocess
import unicodedata

# Third-Party Library Imports
import pefile

# Local Module Imports
from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


def find_casefold_app(apps, app_name):
    """Find an exact application-name match while ignoring letter case."""
    if not app_name:
        return None

    normalized_name = unicodedata.normalize("NFKC", str(app_name)).strip()
    if not normalized_name:
        return None

    for app in apps:
        candidate = unicodedata.normalize(
            "NFKC", str(app.get("name", ""))).strip()
        if candidate == normalized_name:
            return app

    folded_name = normalized_name.casefold()
    if not folded_name:
        return None

    for app in apps:
        candidate = unicodedata.normalize(
            "NFKC", str(app.get("name", ""))).strip().casefold()
        if candidate == folded_name:
            return app
    return None


def is_internet_available():
    """Verifies active internet connectivity by opening a connection to GitHub."""
    try:
        with socket.create_connection(("api.github.com", 443), timeout=2):
            pass
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


def resolve_paf_metadata(app_folder):
    """
    Resolves actual version and launcher executable path for PortableApps (PAF).
    The returned 'exe_path' always points to the main root launcher (start_exe).
    Internal executables/INIs are inspected purely for accurate version determination.
    """
    if not app_folder or not os.path.exists(app_folder):
        return None

    base_meta = get_portable_apps_metadata(app_folder) or {}
    name = base_meta.get('name') or os.path.basename(app_folder)
    start_exe = base_meta.get('start_exe')

    # Root launcher executable path (MUST NOT be overwritten by inner executables)
    launcher_exe_path = (
        os.path.abspath(os.path.join(app_folder, start_exe))
        if start_exe
        else None
    )

    resolved_version = None
    app_dir = os.path.join(app_folder, "App")
    appinfo_dir = os.path.join(app_dir, "AppInfo")

    # 1. Level 1: Check Launcher INI configuration (App/AppInfo/Launcher/*.ini)
    launcher_dir = os.path.join(appinfo_dir, "Launcher")
    if os.path.exists(launcher_dir):
        for file in os.listdir(launcher_dir):
            if file.lower().endswith('.ini'):
                ini_path = os.path.join(launcher_dir, file)
                try:
                    config = configparser.ConfigParser()
                    config.read(ini_path, encoding='utf-8-sig')
                    if config.has_section('Launch'):
                        # Check 64-bit executable first, then 32-bit fallback
                        exe_rel = config.get(
                            'Launch', 'ProgramExecutable64', fallback=None
                        )
                        if not exe_rel or not os.path.exists(
                            os.path.join(app_dir, exe_rel)
                        ):
                            exe_rel = config.get(
                                'Launch', 'ProgramExecutable', fallback=None
                            )

                        if exe_rel:
                            inner_exe = os.path.abspath(
                                os.path.join(app_dir, exe_rel)
                            )
                            if os.path.isfile(inner_exe):
                                resolved_version = get_pe_version(inner_exe)
                except Exception as e:
                    logger.error(
                        f"Error parsing launcher ini {ini_path}: {e}"
                    )
            if resolved_version:
                break

    # 2. Level 2: Check Mozilla application.ini (e.g., Firefox, Thunderbird)
    if not resolved_version and os.path.exists(app_dir):
        for root, dirs, files in os.walk(app_dir):
            if "application.ini" in files:
                app_ini = os.path.join(root, "application.ini")
                try:
                    config = configparser.ConfigParser()
                    config.read(app_ini, encoding='utf-8-sig')
                    if config.has_section('App'):
                        moz_ver = config.get('App', 'Version', fallback=None)
                        if moz_ver:
                            resolved_version = moz_ver
                            break
                except Exception as e:
                    logger.error(
                        f"Error parsing application.ini {app_ini}: {e}"
                    )

    # 3. Level 3: Fallback to DisplayVersion from appinfo.ini
    if not resolved_version:
        resolved_version = base_meta.get('version')

    # Fallback launcher detection if start_exe wasn't specified in appinfo.ini
    if not launcher_exe_path:
        for candidate in [app_folder, app_dir]:
            if os.path.isdir(candidate):
                for f in os.listdir(candidate):
                    if f.lower().endswith(".exe"):
                        launcher_exe_path = os.path.abspath(
                            os.path.join(candidate, f)
                        )
                        break
            if launcher_exe_path:
                break

    return {
        'name': name,
        'version': resolved_version,
        'exe_path': launcher_exe_path,
        'start_exe': start_exe,
    }


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
    Updates the database using resolved PAF metadata.
    Returns a list of updated app records.
    """
    ini_files = scan_ini_files(root_folder)

    updated_apps = []
    for ini_path in sorted(ini_files):
        app_folder = os.path.dirname(
            os.path.dirname(os.path.dirname(ini_path))
        )
        metadata = resolve_paf_metadata(app_folder)
        if not metadata:
            continue

        app_name = metadata.get("name")
        if not app_name:
            continue

        version = metadata.get("version") or "1.0"
        exe_path = metadata.get("exe_path")

        if db and hasattr(db, "add_or_update_app"):
            db.add_or_update_app(
                name=app_name,
                local_path=app_folder,
                exe_path=exe_path,
                current_version=version,
                install_method="paf",
            )

        updated_apps.append({
            "name": app_name,
            "folder": PathManager.to_absolute_path(app_folder),
            "version": version,
            "start_exe": metadata.get("start_exe"),
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
                      or c.isspace() or c in ('-', '_', '.')])
    return " ".join(cleaned.split()).title()


_APP_NAME_SUFFIXES = (
    "_portable", "-portable", ".portable", " portable", " Application",
    " application", " applications", " app", " installer", " install",
    " setup", "x64", "x86", "64bit", "32bit", " beta", " preview",
    " release"
)


def _strip_app_name_suffixes(name):
    cleaned = name
    for suffix in _APP_NAME_SUFFIXES:
        pattern = re.compile(re.escape(suffix) + r'$', re.IGNORECASE)
        cleaned = pattern.sub('', cleaned).strip()
    return cleaned


def get_normalized_app_name(name):
    """
    Processes a raw application name and generates a list of candidate strings ordered by specificity:
    - Candidate 1: Suffixes removed (.portable, -portable, .exe, x64, etc.)
    - Candidate 2: Domain/Brand structure preserved (e.g., draw.io) OR cleaned name
    - Candidate 3: Root keyword before any punctuation (e.g., draw)
    """
    if not name:
        return []

    text = str(name).strip()

    # Special case for Notepad++
    if "notepad++" in text.lower().replace(" ", ""):
        return ["Notepad++"]

    candidates = []

    # Candidate 1: Remove common technical suffixes
    cand1 = _strip_app_name_suffixes(text)

    if cand1:
        candidates.append(cand1)

    # Candidate 2: Preserve brand/domain format (e.g., draw.io) or clean punctuation
    is_domain = bool(re.search(r'\.[a-z]{2,4}$', cand1, re.IGNORECASE))
    if is_domain:
        cand2 = cand1
    else:
        cand2 = re.sub(r'[.\-_]+', ' ', cand1)
        cand2 = " ".join(cand2.split()).title()

    if cand2 and cand2 not in candidates:
        candidates.append(cand2)

    # Candidate 3: Extract root keyword before first punctuation symbol (., -, _, space)
    root_match = re.split(r'[.\-_ ]', cand1)
    if root_match and root_match[0]:
        cand3 = root_match[0].strip()
        if cand3 and cand3 not in candidates:
            candidates.append(cand3)

    return candidates


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
    """
    Extracts raw application name from PE executable metadata using standard hierarchy:
    1. ProductName
    2. FileDescription
    3. OriginalFilename (without .exe extension)
    """
    product_name = None
    file_desc = None
    original_fn = None

    pe = None
    try:
        pe = pefile.PE(file_path)
        if hasattr(pe, 'FileInfo'):
            for file_info in pe.FileInfo:
                for info_block in file_info:
                    if hasattr(info_block, 'StringTable'):
                        for entry in info_block.StringTable:
                            for key, value in entry.entries.items():
                                key_str = key.decode('utf-8', errors='ignore')
                                val_str = value.decode(
                                    'utf-8', errors='ignore').strip()

                                if key_str == 'ProductName' and val_str:
                                    product_name = val_str
                                elif key_str == 'FileDescription' and val_str:
                                    file_desc = val_str
                                elif key_str == 'OriginalFilename' and val_str:
                                    original_fn = val_str
    except Exception as e:
        logger.error(f"Error loading PE metadata from {file_path}: {e}")
    finally:
        if pe:
            pe.close()

    # Preserve the metadata priority while removing common technical suffixes.
    name = product_name or file_desc
    if not name and original_fn:
        name = re.sub(r'(?i)\.exe$', '', original_fn).strip()
    if name:
        return _strip_app_name_suffixes(name) or name
    return None


def is_app_running(folder_path):
    """Checks if any executable (.exe) inside the target folder is currently running on Windows."""
    if not folder_path or not os.path.exists(folder_path):
        return False

    # Collect all .exe file names in the target directory
    exe_names = set()
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".exe"):
                exe_names.add(file.lower())

    if not exe_names:
        return False

    try:
        # Hide standard console window during process execution on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Query running Windows processes
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            startupinfo=startupinfo,
            check=True
        )

        output_lower = result.stdout.lower()

        # Match running executables against target folder executables
        for exe_name in exe_names:
            if f'"{exe_name}"' in output_lower:
                logger.info(f"Detected running process: {exe_name}")
                return True

    except Exception as e:
        logger.error(
            f"Error checking running processes for {folder_path}: {e}")

    return False
