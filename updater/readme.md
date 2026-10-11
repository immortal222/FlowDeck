# FlowDeck Updater

A lightweight, standalone helper module designed to handle automated background updates for **FlowDeck** on Windows.

---

## 📌 Overview

The FlowDeck Updater operates independently of the main application. When a new version is downloaded and extracted, the main `FlowDeck.exe` application launches `updater.exe` from a temporary extraction directory and terminates itself. 

The updater then waits for the main process to unlock files, replaces the existing application assets/binaries with the new version, and restarts `FlowDeck.exe`.

---

## ⚙️ How It Works

1. **Invocation:** `FlowDeck.exe` extracts the update release package into a temporary directory containing `updater.exe` and `update_config.json`.
2. **Process Wait & File Unlock:** The updater reads `update_config.json` to identify the target installation path and executable name, ensuring `FlowDeck.exe` has fully exited.
3. **File Replacement:** Copies updated files to the destination directory while handling retry loops for potential Windows file locks.
4. **Relaunch:** Launches the newly updated `FlowDeck.exe` and creates an `update_flag.json` to signal a successful update on startup.

---

## 🛠️ Building `updater.exe`

To compile `updater.py` into a standalone executable using **PyInstaller**, navigate to the `updater/` directory and run:

```bash
pyinstaller --noconfirm --clean --onefile --windowed --icon="app_icon.ico" --name "updater" updater.py