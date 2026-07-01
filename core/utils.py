from ast import Import
import configparser
import os
import re
import shutil
import socket

import pefile

from core.services.path_manager import PathManager


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


def is_update_available(current_ver, latest_ver):
    """Compares version strings and returns True if an update is available."""
    if not latest_ver or latest_ver == "Unknown":
        return False

    # Clean 'v' prefix and whitespace
    c = str(current_ver).strip().lower().lstrip('v')
    l = str(latest_ver).strip().lower().lstrip('v')

    try:
        # Numeric comparison of version components
        c_parts = [int(x) for x in c.split('.') if x.isdigit()]
        l_parts = [int(x) for x in l.split('.') if x.isdigit()]
        return l_parts > c_parts
    except:
        # Fallback to simple string comparison
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
    print(f"[DEBUG] Searching for appinfo.ini at path: {app_folder}")
    ini_path = os.path.join(app_folder, "App", "AppInfo", "appinfo.ini")

    if not os.path.exists(ini_path):
        print(f"[DEBUG] File NOT found at path.")
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
            print(
                f"[DEBUG] Found metadata in appinfo.ini - Name: {name}, Version: {version}, EXE: {start_exe}")
            return {
                'name': name,
                'version': version,
                'start_exe': start_exe
            }
        else:
            print(
                f"[DEBUG] Insufficient metadata found. Sections: {config.sections()}")
    except Exception as e:
        print(f"[UTILS] Error reading {ini_path}: {e}")

    return None


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


def get_safe_folder_path(base_dir, desired_name, current_path=None):
    """
    Generates a system-safe directory path based on application name.
    Handles naming conflicts by appending numeric suffixes.
    """
    safe_folder_name = re.sub(r'[\\/*?:"<>|]', "", desired_name).strip()
    new_dir_path = os.path.join(base_dir, safe_folder_name).replace("\\", "/")

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
        print("ℹ️ Module 'pefile' missing. Run: pip install pefile")
    except Exception:
        pass
    return None


def get_pe_name(file_path):
    try:
        pe = pefile.PE(file_path)
        if not hasattr(pe, 'FileInfo'):
            print("No version info found")

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
                                return value.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error loading file: {e}")
    finally:
        pe.close()
    return None
