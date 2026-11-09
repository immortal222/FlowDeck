import logging
import sys

logger = logging.getLogger(__name__)


def remove_legacy_startup_entry():
    """Removes the 'FlowDeck' autostart value left by older versions (one-time cleanup)."""
    if sys.platform != "win32":
        return

    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "FlowDeck")
            logger.info("Removed legacy FlowDeck startup entry.")
    except FileNotFoundError:
        # No entry present: nothing to clean up.
        pass
    except Exception as e:
        logger.warning(f"Could not remove legacy startup entry: {e}")
