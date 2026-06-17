import json
import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

from core.services.path_manager import PathManager
from core.services.single_instance import SingleInstance
from locales.localization import _manager
from ui.main_window import AppMainWindow


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("=== FlowDeck Start===")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 1. Read config for language at startup
    config_path = PathManager.get_config_path()
    current_lang = "Ελληνικά"  # default if file doesn't exist

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                current_lang = config_data.get("language", "Ελληνικά")
        except Exception as e:
            print(f"Error reading config in main: {e}")

    # 2. Activate language in manager
    _manager.set_language(current_lang)

    # 3. --- SINGLE INSTANCE CHECK ---
    instance = SingleInstance()
    if instance.is_running:
        logger.info(
            "Application is already running! Signal sent to wake up. Exiting...")
        sys.exit(0)

    # 4. --- GUI LOADING ---
    window = AppMainWindow()
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
