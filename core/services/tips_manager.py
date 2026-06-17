import json
import logging
import os
import random

from core.services.path_manager import PathManager
from locales.localization import get_current_lang
from ui.styles.styles import TIPS_THEMES

logger = logging.getLogger(__name__)


class TipsManager:
    """Manages the random selection and rendering of helpful tips on the Dashboard."""

    def __init__(self, ui_widget):
        self.ui_widget = ui_widget

        # Tips file location resolved via PathManager
        self.json_path = PathManager.get_tips_path()

        # Enable automatic text wrapping
        if self.ui_widget:
            self.ui_widget.setWordWrap(True)

    def load_and_render_tips(self):
        """Selects a random tip and renders it using HTML with Word Wrap."""
        if not self.ui_widget:
            return

        try:
            if not os.path.exists(self.json_path):
                self.ui_widget.setText("The tips.json file was not found.")
                return

            with open(self.json_path, "r", encoding="utf-8") as f:
                all_tips_data = json.load(f)
                # Retrieve tips for the current language with Greek fallback
                tips_list = all_tips_data.get(
                    get_current_lang(), all_tips_data.get("el", []))

            if not tips_list:
                self.ui_widget.setText("No tips available.")
                return

            # Select a random tip from the list
            selected_tip = random.choice(tips_list)

            # Apply theme-specific text coloring
            theme_name = "Modern Dark"
            config_path = PathManager.get_config_path()
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        theme_name = json.load(f).get("theme", "Modern Dark")
                except:
                    pass

            txt_color = TIPS_THEMES.get(theme_name, "#DBE5EB")

            # Render clean HTML for QLabel to maintain consistent wrapping
            html = f"""
            <p style="font-family: 'Segoe UI', sans-serif; color: {txt_color}; margin: 0px; line-height: 14px; font-size: 12px;">
                {selected_tip['text']}
            </p>
            """
            self.ui_widget.setText(html)
        except Exception as e:
            logger.error(f"Error loading tips: {e}")
            self.ui_widget.setText("Error loading tips.")
