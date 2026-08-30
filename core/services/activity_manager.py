import json
import logging
import os
from datetime import datetime

from locales.localization import _
from core.services.config_manager import ConfigManager
from core.services.path_manager import PathManager
from ui.styles.styles import ACTIVITY_THEMES

logger = logging.getLogger(__name__)


class ActivityManager:
    """Handles logging and rendering of the application activity timeline."""

    def __init__(self, config_manager=None):
        self.ui_widget = None
        self.config = config_manager if config_manager is not None else ConfigManager()
        self.log_file = PathManager.get_log_path()
        self.events = self.load_events()

    def load_events(self):
        """Loads events from the local JSON log file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                if self.ui_widget:
                    self.log(_("act_err_load_log", "❌ Failed to load activity history: {error}").format(
                        error=e), "error")
        return []

    def save_events(self):
        """Saves current events to the local JSON log file."""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.events, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving activity log: {e}")
            if self.ui_widget:
                self.log(_("act_err_save_log", "❌ Failed to save activity history: {error}").format(
                    error=e), "error")

    def set_ui_widget(self, widget):
        """Links the manager to a UI widget for rendering."""
        self.ui_widget = widget
        self.refresh_ui()

    def get_relative_time_text(self, timestamp_str):
        """Converts a timestamp string into a human-readable relative time (e.g., '2 hours ago')."""
        try:
            event_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - event_time

            seconds = diff.total_seconds()
            days = diff.days

            if seconds < 60:
                return _("act_time_just_now", "Just now")

            elif seconds < 3600:
                minutes = int(seconds // 60)
                if minutes > 1:
                    return _("act_time_minutes_ago", "{minutes} minutes ago").format(minutes=minutes)
                return _("act_time_minute_ago", "1 minute ago")

            elif days == 0:
                hours = int(seconds // 3600)
                if hours > 1:
                    return _("act_time_hours_ago", "{hours} hours ago").format(hours=hours)
                return _("act_time_hour_ago", "1 hour ago")

            elif days == 1:
                return _("act_time_yesterday", "Yesterday")

            else:
                return _("act_time_days_ago", "{days} days ago").format(days=days)

        except Exception:
            return _("act_time_some_time_ago", "Some time ago")

    def log(self, message_key, event_type="launch", params=None):
        """Logs a new event and updates the history."""
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Map event types to specific icons
        if event_type == "install":
            icon_file = "icons/activity_install.png"
        elif event_type == "update":
            icon_file = "icons/activity_update.png"
        elif event_type == "error":
            icon_file = "icons/activity_error.png"
        elif event_type == "reset":
            icon_file = "icons/activity_reset.png"
        else:
            icon_file = "icons/activity_launch.png"

        if isinstance(params, dict):
            clean_params = params
        elif isinstance(params, str):
            clean_params = {"app_name": params}
        else:
            clean_params = {}

        new_event = {
            "icon_path": PathManager.get_asset_path(icon_file),
            "message_key": message_key,
            "params": clean_params,
            "message": message_key,
            "timestamp": current_timestamp
        }

        self.events.insert(0, new_event)

        if len(self.events) > 10:
            self.events = self.events[:10]

        self.save_events()
        self.refresh_ui()

    def refresh_ui(self):
        """Renders the activity timeline as HTML in the UI widget."""
        if not self.ui_widget:
            return

        # Load current theme for timeline colors
        theme_name = self.config.get("theme", "Modern Dark")

        theme_data = ACTIVITY_THEMES.get(
            theme_name, ACTIVITY_THEMES["Modern Dark"])
        txt_color = theme_data.get("timeline_text", "#DBE5EB")
        time_color = theme_data.get("timeline_time", "#888888")
        logger.debug(
            f"Applying activity theme: {theme_name} with text color {txt_color} and time color {time_color}")

        self.ui_widget.setStyleSheet(
            "QTextEdit {  border: none; }"
        )
        html_content = "<div style='font-family: \"Segoe UI\", sans-serif; padding: 10px; ;'>"

        # Retrieve absolute path for line resource
        line_raw_path = PathManager.get_asset_path("icons/line.png")
        line_url = f"file:///{line_raw_path}"

        for i, ev in enumerate(self.events):
            t_stamp = ev.get(
                "timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            relative_time = self.get_relative_time_text(t_stamp)

            is_last = (i == len(self.events) - 1)

            # Translation logic
            m_key = ev.get("message_key")
            m_params = ev.get("params", {})
            if isinstance(m_params, str):
                m_params = {"app_name": m_params}
            elif not isinstance(m_params, dict):
                m_params = {}

            if m_key:
                try:
                    display_text = _(m_key, m_key).format(**m_params)
                except Exception:
                    display_text = _(m_key, m_key)
            else:
                display_text = ev.get('message', 'Unknown Event')

            # Load icons
            raw_path = ev.get('icon_path', '')
            if raw_path and not raw_path.startswith('file:///'):
                icon_url = f"file:///{raw_path}"
            else:
                icon_url = raw_path

            if not is_last:
                line_html = f'<img src="{line_url}" width="2" height="30" style="display: block; margin: 4px auto; padding-bottom: 4px;" />'
            else:
                line_html = '<div style="height: 38px;"></div>'

            html_content += f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="background: transparent; margin-bottom: 0px; border-collapse: collapse;">
                <tr>
                    <td width="24" valign="top" align="center" style="padding: 0px; margin: 0px; text-align: center;">
                        <img src="{icon_url}" width="24" height="24" style="display: block; margin: 0 auto;" />
                        {line_html}
                    </td>
                    
                    <td valign="top" style="padding-left: 15px; padding-top: 2px; padding-bottom: 25px; text-align: left;">
                        <div style="font-size: 13px; font-weight: 500; color: {txt_color}; margin-bottom: 4px;">
                            {display_text} 
                        </div>
                        <div style="font-size: 11px; color: {time_color};">
                            {relative_time}
                        </div>
                    </td>
                </tr>
            </table>
            """

        html_content += "</div>"

        self.ui_widget.clear()
        self.ui_widget.setHtml(html_content)

    def clear_history(self):
        """Clears all activity history and updates the UI."""
        self.events = []
        self.save_events()
        self.refresh_ui()
