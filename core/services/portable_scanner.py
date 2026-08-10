import logging
import os
import re
from pathlib import Path

from core.utils import get_clean_app_name, get_normalized_app_name, get_pe_name, get_pe_version, get_portable_apps_metadata

logger = logging.getLogger(__name__)


class PortableScanner:
    """Scans a portable application folder and extracts candidate metadata."""

    EXCLUDE_NAMES = {
        "uninstall.exe", "uninst.exe", "setup.exe", "install.exe",
        "updater.exe", "update.exe", "crashreporter.exe",
        "helper.exe", "vc_redist.exe", "dxsetup.exe", "config.exe",
        "dependencies.exe", "unins000.exe", "unins001.exe", "elevate.exe"
    }

    def __init__(self, max_search_depth=2):
        self.max_search_depth = max_search_depth

    def find_main_executable(self, folder_path):
        folder = Path(folder_path)
        if not folder.is_dir():
            return None

        candidates = []
        folder_name_lower = folder.name.lower()

        try:
            for entry in folder.iterdir():
                if entry.is_file() and entry.suffix.lower() == ".exe":
                    if entry.name.lower() not in self.EXCLUDE_NAMES:
                        candidates.append(
                            (entry.resolve(), entry.name, entry.stat().st_size, True))
        except Exception:
            pass

        if not candidates:
            for root, _, files in os.walk(folder_path):
                root_path = Path(root)
                depth = len(root_path.relative_to(folder).parts)
                if depth > self.max_search_depth:
                    continue
                for file_name in files:
                    if file_name.lower().endswith(".exe") and file_name.lower() not in self.EXCLUDE_NAMES:
                        full_path = root_path / file_name
                        candidates.append(
                            (full_path.resolve(), file_name, full_path.stat().st_size, depth == 0))

        if not candidates:
            return None

        best_candidate = None
        best_score = -1

        for path, name, size, is_root in candidates:
            name_no_ext = Path(name).stem.lower()
            score = 0
            if name_no_ext in folder_name_lower or folder_name_lower in name_no_ext:
                score += 50
            if is_root:
                score += 30
            score += min(20, int(size / (1024 * 1024)))

            if score > best_score:
                best_score = score
                best_candidate = path

        return str(best_candidate) if best_candidate else None

    def extract_name_and_version(self, folder_path):
        folder = Path(folder_path)
        folder_name = folder.name

        clean_name = folder_name
        for token in [
            "_portable", "-portable", ".portable", " portable", " Application",
            "Aplication", " application", " applications", " app",
            " installer", " install", " setup", "x64", "x86",
            "64bit", "32bit", " beta", " preview", " release"
        ]:
            clean_name = clean_name.replace(token, "")

        version_pattern = r'[-_]v?(\d+\.\d+(?:\.\d+)?(?:[-_][a-zA-Z0-9]+)?)'
        match = re.search(version_pattern, clean_name, re.IGNORECASE)

        if match:
            version = match.group(1)
            name_part = clean_name[:match.start()]
            name = name_part.replace("-", " ").replace("_", " ").strip()
            return get_normalized_app_name(name), version

        main_exe = self.find_main_executable(folder_path)
        pe_version = None
        pe_name = None

        if main_exe and os.path.exists(main_exe):
            pe_version = get_pe_version(main_exe)
            pe_name = get_pe_name(main_exe)

        version = pe_version or "1.0.0"
        name = get_normalized_app_name(
            pe_name) if pe_name else get_normalized_app_name(clean_name)
        return name, version

    def scan_folder_metadata(self, folder_path):
        folder = Path(folder_path)
        if not folder.is_dir():
            return None

        metadata = get_portable_apps_metadata(folder_path)
        is_paf = False
        exe_path = None
        guessed_name = None
        guessed_version = None

        if metadata:
            is_paf = True
            guessed_name = metadata.get("name") or folder.name
            guessed_version = metadata.get("version") or "1.0.0"
            start_exe = metadata.get("start_exe")
            if start_exe:
                exe_path = (folder / start_exe).resolve()
                if not exe_path.exists():
                    exe_path = None

        if not exe_path:
            exe_path = self.find_main_executable(folder_path)

        if not exe_path:
            return None

        if not guessed_name or not guessed_version:
            extracted_name, extracted_version = self.extract_name_and_version(
                folder_path)
            guessed_name = guessed_name or extracted_name
            guessed_version = guessed_version or extracted_version

        return {
            "name": get_normalized_app_name(guessed_name),
            "version": guessed_version,
            "exe_path": str(Path(exe_path).resolve()).replace("\\", "/"),
            "is_paf": is_paf,
            "source_hint": "paf" if is_paf else "manual"
        }
