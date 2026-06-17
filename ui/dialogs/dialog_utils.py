import logging

from PyQt5.QtWidgets import QMessageBox

from ui.styles.styles import DIALOG_LIGHT_STYLE, DIALOG_STYLE

logger = logging.getLogger(__name__)


def create_styled_msgbox(parent, title, text, is_warning=False):
    """Creates and returns a uniformly styled QMessageBox based on the current theme."""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(QMessageBox.Warning if is_warning else QMessageBox.Information)

    if is_warning:
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
    else:
        msg.setStandardButtons(QMessageBox.Ok)

    # Resolve theme dynamically from configuration
    theme = "Modern Dark"
    if parent and hasattr(parent, 'settings_controller'):
        theme = parent.settings_controller.config.get("theme", "Modern Dark")
    elif hasattr(parent, 'main_window'):
        theme = parent.main_window.settings_controller.config.get(
            "theme", "Modern Dark")

    style = DIALOG_LIGHT_STYLE if theme == "Modern Light" else DIALOG_STYLE
    msg.setStyleSheet(style)

    logger.info(f"Dialog created: '{title}' with theme: {theme}")

    return msg


def show_info(parent, title, text):
    """Displays a styled information dialog."""
    return create_styled_msgbox(parent, title, text, False).exec_()


def ask_confirmation(parent, title, text):
    """Displays a styled confirmation dialog and returns True if 'Yes' is clicked."""
    return create_styled_msgbox(parent, title, text, True).exec_() == QMessageBox.Yes
