import logging
import os
import shutil
import subprocess
import sys

from core.services.path_manager import PathManager

logger = logging.getLogger(__name__)


class AppInstaller:
    """Handles extraction, hoisting, and installation of portable applications."""

    def __init__(self, portable_root_path):
        self.portable_root = portable_root_path

    def contains_exe(self, archive_path):
        """Checks if the archive contains at least one executable file using 7za."""
        try:
            seven_z_exe = PathManager.get_bin_path("7za.exe")
            if not os.path.exists(seven_z_exe):
                return True  # Fallback if 7za is missing to avoid blocking execution

            result = subprocess.run(
                [seven_z_exe, 'l', archive_path],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return '.exe' in result.stdout.lower()
        except Exception as e:
            logger.error(f"Error checking archive contents: {e}")
            return True

    def install_from_zip(self, archive_path, app_name):
        """Extracts archive to a temporary directory and moves it to the final destination."""
        final_target_dir = os.path.join(self.portable_root, app_name)
        temp_dir = final_target_dir + "_temp_extract"

        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            logger.info(f"Extracting {archive_path} using 7za.exe...")

            seven_z_exe = PathManager.get_bin_path("7za.exe")
            if not os.path.exists(seven_z_exe):
                raise FileNotFoundError(
                    "7za.exe not found in bin directory.")

            cmd = [seven_z_exe, 'x', archive_path, f'-o{temp_dir}', '-y']

            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd, startupinfo=startupinfo, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"7-Zip error: {result.stderr}")

            self._hoist_nested_folder(temp_dir)

            if not os.path.exists(final_target_dir):
                os.makedirs(final_target_dir)

            for item in os.listdir(temp_dir):
                src_path = os.path.join(temp_dir, item)
                dst_path = os.path.join(final_target_dir, item)
                if os.path.exists(dst_path):
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                shutil.move(src_path, dst_path)

            shutil.rmtree(temp_dir)
            return final_target_dir

        except Exception as e:
            logger.error(f"Installation error: {e}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return None

    def _hoist_nested_folder(self, target_dir):
        """Recursively lifts contents from single nested subdirectories to the root directory."""
        while True:
            items = os.listdir(target_dir)
            ignored = ['desktop.ini', 'thumbs.db', '.ds_store']
            valid_items = [i for i in items if i.lower() not in ignored]

            dirs = [i for i in valid_items if os.path.isdir(
                os.path.join(target_dir, i))]
            files = [i for i in valid_items if os.path.isfile(
                os.path.join(target_dir, i))]

            if len(dirs) == 1 and len(files) == 0:
                nested_path = os.path.join(target_dir, dirs[0])
                logger.info(
                    f"Detected nested folder: '{dirs[0]}'. Hoisting contents...")

                for sub_item in os.listdir(nested_path):
                    src = os.path.join(nested_path, sub_item)
                    dst = os.path.join(target_dir, sub_item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, target_dir)
                shutil.rmtree(nested_path, ignore_errors=True)
            else:
                break
