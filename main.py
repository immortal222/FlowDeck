# Standard Library Imports
import os
import sys
import traceback

# Third-Party Library Imports
from PyQt5.QtWidgets import QApplication

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

# Local Module Imports
from core.logging_config import setup_logging
from core.services.config_manager import ConfigManager
from core.services.path_manager import PathManager
from core.services.single_instance import SingleInstance
from locales.localization import _manager
from ui.main_window import AppMainWindow


def _write_last_resort_trace(message):
    try:
        log_dir = PathManager.to_absolute_path('logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'flowdeck_debug_trace.log')
        with open(log_file, 'a', encoding='utf-8') as handle:
            handle.write(message + '\n')
    except Exception:
        pass


def _install_exception_hook():
    def _handle_exception(exc_type, exc_value, exc_traceback):
        try:
            if issubclass(exc_type, KeyboardInterrupt):
                return
            error_text = ''.join(traceback.format_exception(
                exc_type, exc_value, exc_traceback))
            _write_last_resort_trace(
                f"[MAIN] Unhandled exception:\n{error_text}")
            print(error_text, file=sys.stderr)
        except Exception:
            pass

    sys.excepthook = _handle_exception


def _cleanup_leftover_updater():
    clean_updater_file = PathManager.to_absolute_path('updater.exe')
    try:
        if os.path.exists(clean_updater_file):
            os.remove(clean_updater_file)
            logger.info("Cleaned up leftover updater.exe")
    except Exception as e:
        logger.error(f"Error during cleanup updater.exe. {e}")


if __name__ == "__main__":
    _install_exception_hook()
    logger = setup_logging()
    logger.info("=== FlowDeck Start===")

    # Clean up leftover updater.exe if present
    _cleanup_leftover_updater()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 1. Load centralized application config
    config_manager = ConfigManager()
    _manager.set_language(config_manager.get("language", "English"))

    # 2. --- SINGLE INSTANCE CHECK ---
    instance = SingleInstance()
    if instance.is_running:
        logger.info(
            "Application is already running! Signal sent to wake up. Exiting...")
        sys.exit(0)

    # 4. --- GUI LOADING ---
    window = AppMainWindow(config_manager=config_manager)
    window.show()

    # 5. --- HANDLE APP "WAKE UP" ---
    def bring_to_front():
        logger.info("Received signal: Bringing window to front!")
        window.showNormal()
        window.activateWindow()

        # Return to Dashboard by clicking the menu button
        if hasattr(window, 'ui') and hasattr(window.ui, 'btn_pageHome'):
            window.ui.btn_pageHome.setChecked(True)
            window.ui.btn_pageHome.click()

    # Connect server signal to function
    instance.show_main_window.connect(bring_to_front)

    sys.exit(app.exec_())
