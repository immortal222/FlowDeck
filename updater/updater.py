# Standard Library Imports
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

# Third-Party Library Imports
import psutil


class CopyWorker(threading.Thread):
    """
    Background worker thread using Standard Python threading to wait 
    for the main process exit and copy updated files to the target directory.
    """

    def __init__(self, source_dir, target_dir, exe_name, config_path, update_ui_callback, finish_callback):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.exe_name = exe_name
        self.config_path = config_path
        self.update_ui_callback = update_ui_callback
        self.finish_callback = finish_callback

    def run(self):
        try:
            # Step 1: Wait for main application process to terminate completely
            self.update_ui_callback(0, "Waiting for application to close...")
            max_wait_seconds = 10
            waited = 0

            while waited < max_wait_seconds:
                process_found = False
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'] and proc.info['name'].lower() == self.exe_name.lower():
                            process_found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                if not process_found:
                    break

                time.sleep(1)
                waited += 1

            # Give the USB drive an extra second to release file locks
            time.sleep(1.5)

            # Step 2: Build file list for copy progress calculation
            all_files = []
            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))

            total_files = len(all_files)
            if total_files == 0:
                self.finish_callback(
                    False, "No files found to copy in update package.")
                return

            # Explicit list of excluded filenames
            excluded_names = {
                os.path.basename(self.config_path).lower().strip(),
                "updater.exe",
                "updater",
                "updater.exe.manifest",
            }
            current_binary = os.path.basename(sys.argv[0]).lower().strip()
            excluded_names.add(current_binary)

            # Step 3: Copy/overwrite files with status updates
            for index, s_item in enumerate(all_files, start=1):
                rel_path = os.path.relpath(s_item, self.source_dir)
                d_item = os.path.join(self.target_dir, rel_path)

                item_clean = os.path.basename(s_item).lower().strip()
                if item_clean in excluded_names:
                    continue

                progress_val = int((index / total_files) * 100)
                self.update_ui_callback(progress_val, f"Copying: {rel_path}")

                os.makedirs(os.path.dirname(d_item), exist_ok=True)
                shutil.copy2(s_item, d_item)

            # Step 4: Write update_flag.json in target directory with version info
            version_str = "latest"
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        version_str = cfg.get("version", "latest")
                except Exception:
                    pass

            flag_data = {
                "updated": True,
                "version": version_str
            }
            flag_path = os.path.join(self.target_dir, "update_flag.json")
            with open(flag_path, "w", encoding="utf-8") as f:
                json.dump(flag_data, f, indent=4)

            self.finish_callback(True, "Update completed successfully.")

        except Exception as e:
            self.finish_callback(False, str(e))


class UpdaterApp:
    """
    Main Tkinter GUI Application for the lightweight updater.
    """

    def __init__(self, root, source_dir, target_dir, exe_name, config_path):
        self.root = root
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.exe_name = exe_name
        self.config_path = config_path

        self.setup_ui()
        self.start_worker()

    def setup_ui(self):
        self.root.title("FlowDeck Update")

        # Set fixed window size
        window_width = 400
        window_height = 120

        # Calculate coordinates to center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        # Set geometry with position coordinates
        self.root.geometry(
            f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), "app_icon.ico")
        if not os.path.exists(icon_path):
            icon_path = "app_icon.ico"

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Main container with padding
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(
            frame, text="Initializing update...", wraplength=370)
        self.status_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", mode="determinate", maximum=100)
        self.progress_bar.pack(fill=tk.X, expand=True)

    def update_ui(self, progress_val, status_text):
        # Schedule GUI updates safely on the main thread
        self.root.after(0, self._apply_ui, progress_val, status_text)

    def _apply_ui(self, progress_val, status_text):
        self.progress_bar['value'] = progress_val
        self.status_label.config(text=status_text)

    def finish_callback(self, success, message):
        self.root.after(0, self._apply_finish, success, message)

    def _apply_finish(self, success, message):
        if success:
            main_exe = os.path.join(self.target_dir, self.exe_name)
            if os.path.exists(main_exe):
                subprocess.Popen([main_exe], cwd=self.target_dir)
            self.root.destroy()
        else:
            messagebox.showerror(
                "Update Failed", f"Failed to apply update:\n{message}")
            self.root.destroy()

    def start_worker(self):
        worker = CopyWorker(
            self.source_dir,
            self.target_dir,
            self.exe_name,
            self.config_path,
            self.update_ui,
            self.finish_callback
        )
        worker.daemon = True
        worker.start()


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        sys.exit(1)

    source_dir = config.get("source_dir")
    target_dir = config.get("target_dir")
    exe_name = config.get("exe_name")

    if not source_dir or not target_dir or not exe_name:
        sys.exit(1)

    root = tk.Tk()
    app = UpdaterApp(root, source_dir, target_dir, exe_name, config_path)
    root.mainloop()


if __name__ == "__main__":
    main()
