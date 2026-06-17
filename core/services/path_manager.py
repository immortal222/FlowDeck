import os
import sys


class PathManager:
    """Handles centralized path resolution for application resources, configuration, and data."""

    @staticmethod
    def get_root_dir():
        """Returns the application's root directory."""
        if getattr(sys, 'frozen', False):
            # Running as a bundled EXE via PyInstaller
            return os.path.dirname(sys.executable)
        else:
            # Running as a standard Python script
            return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    @staticmethod
    def get_resource_path(relative_path):
        """
        Resolves the correct path for resources (assets, locales, etc.),
        handling differences between development and bundled environments.
        """
        if hasattr(sys, '_MEIPASS'):
            # Bundled environment (sys._MEIPASS)
            base = sys._MEIPASS
        else:
            # Development environment
            base = PathManager.get_root_dir()

        return os.path.join(base, relative_path).replace("\\", "/")

    @staticmethod
    def get_asset_path(relative_path):
        """Returns the absolute path for an asset resource."""
        return PathManager.get_resource_path(os.path.join("assets", relative_path))

    @staticmethod
    def get_bin_path(exe_name):
        """Returns the path for a binary executable located in the bin folder."""
        return PathManager.get_resource_path(os.path.join("bin", exe_name))

    @staticmethod
    def get_config_path():
        """Returns the path for the configuration file."""
        # Config file resides next to the executable to maintain portability
        return os.path.join(PathManager.get_root_dir(), "config.json").replace("\\", "/")

    @staticmethod
    def get_database_path(db_name="linkweave.db"):
        """Returns the path for the SQLite database file."""
        # Database resides next to the executable
        return os.path.join(PathManager.get_root_dir(), db_name).replace("\\", "/")

    @staticmethod
    def get_log_path(log_name="activity_log.json"):
        """Returns the path for the JSON activity log."""
        return os.path.join(PathManager.get_root_dir(), log_name).replace("\\", "/")

    @staticmethod
    def get_tips_path():
        """Returns the path for the tips.json resource file."""
        return PathManager.get_resource_path("tips.json")
