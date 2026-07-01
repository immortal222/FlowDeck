# 🚀 FlowDeck

> **Smart Portable Apps Manager & Dashboard for Windows**
> *Organize, launch, and automatically update portable applications without bloating your operating system.*

---

![Windows](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue?style=for-the-badge)

## 📌 What is FlowDeck?

**FlowDeck** is an intelligent, modern dashboard designed specifically for portable applications on Windows. It organizes, installs, runs safely, and checks for updates—all while keeping your operating system 100% clean from registry entries and leftover file clutter.

It bridges the gap between the clean nature of portable software and the seamless package management offered by CLI tools like Scoop, wrapping everything in a beautiful, fast GUI built with **PyQt5**.

---

## 🛠️ The 4 Core Pillars

### 1. 📂 "Portable Only" Philosophy
FlowDeck rejects traditional, system-wide software installations. Everything is kept isolated inside a central directory (`portable_root`) defined by the user. If you copy this directory to a USB drive, you take all your applications, personal configurations, and app data with you, ready to run on any Windows computer.

### 2. 🧠 Smart Installation Wizard
The built-in installation wizard dynamically recognizes and automates the setup of different file formats:
* **ZIP / 7Z Archives:** Automatically parses the file name, guesses the application name and version using advanced regex matching, extracts the contents, and guides the user to select the primary executable (`.exe`).
* **Official PortableApps (`.paf.exe`) Installers:** Applies smart automation. It copies the installer to your portable directory. It waits user to make the installation, reads the `appinfo.ini` file to extract app metadata (name, version), and automatically deletes the temporary installer file to save disk space.

### 🌐 3. Online Repositories Integration (Scoop API & Chocolatey)
Once an application is detected, FlowDeck communicates with the **Scoop API** and local indices in the background. It matches human-readable names to official app IDs and retrieves rich online metadata:
* Official homepages.
* The latest available version released online to enable instant update checking.

### ⚡ 4. Independent Launch & Process Management
* **Detached App Execution:** Applications are launched using specific Windows flags (`creationflags=0x00000008`) and a sanitized environment variable map (`env=clean_env`). This prevents Qt runtime conflicts (essential for Qt apps like XnConvert) and guarantees that closing FlowDeck will never crash or close your running apps.
* **Minimize to Tray:** Closing the main window (`X`) hides the app to the Windows System Tray with a clean notification, keeping your workspace neat. Selecting "Exit" clears the tray icons and cleanly terminates all background processes.

---

## 🎯 Why FlowDeck? (The Unique Selling Point)

| Feature | Classic Windows Apps | Traditional Portable | FlowDeck 🚀 |
| :--- | :---: | :---: | :---: |
| **Registry & System Bloat** | ❌ Yes (Bloats) |  Clean |  Clean |
| **Central Management** | ❌ No | ❌ No (Scattered folders) |  Yes |
| **Automatic Metadata / URLs** | ❌ No | ❌ No |  Yes (Via Scoop) |
| **Instant Update Checks** |  Via individual installers | ❌ Manual |  Automatic |
| **Full Portability (USB)** | ❌ No |  Yes |  Yes (1-Click) |

---

## 📁 Project Structure

```text
FlowDeck/
│
├── main.py                     # Primary entry point of the application
├── linkweave.db                # SQLite Database (storing apps, paths, and favorites)
│
├── core/                       # Core business logic
│   ├── api/                    # Scoop & Chocolatey API connectors
│   ├── services/               # Database, Activity, Path & Update Managers
│   └── utils.py                # Helper utilities (Disk stats, version comparators, file sizes)
│
├── ui/                         # User Interface layer (PyQt5)
│   ├── generated/              # Compiled UI files from Qt Designer
│   ├── pages/                  # Controllers for pages (Dashboard, Library, Settings)
│   └── styles/                 # Theme configurations (Modern Dark / Light CSS)
│
└── locales/                    # Localization files (Full English and Greek support)
```

## 🚀 Getting Started (For Developers)

  1.Clone the repository:

```
git clone https://github.com/immortal222/FlowDeck.git
cd FlowDeck
```

  2. Create a virtual environment (Recommended):

```
python -m venv venv
venv\Scripts\activate
```

  3. Install the required dependencies:

```
pip install -r requirements.txt
```

  4. Run the application:

```
python main.py
```

## 🔒 Licensing & Third-Party Tools

FlowDeck acts as an orchestrator (wrapper) and respects the licenses of the CLI utilities it triggers externally:

* Scoop CLI (MIT License) - Reading JSON manifests and buckets.
* Chocolatey CLI (Apache License 2.0) - Managing system packages.
* 7-Zip (GNU LGPL) - External executable used for Ultra compression/decompression on backups.

FlowDeck itself is released under the GNU GPLv3 License. Feel free to use, modify, and contribute to this project!
## 🗺️ Roadmap (TODO)

* Implement 1-Click Update for ZIP-based applications directly from the UI.
* Add a background scheduler for automatic orphan folder detection.
* Enrich the HTML Activity Timeline with interactive statistical charts.

## Acknowledgements / Credits
* Developed with the assistance of **Google Gemini**, which helped with code generation, structuring, and troubleshooting.


### 🛡️ Windows Defender / Antivirus Warning (False Positive)
As this application is packaged into a standalone executable using PyInstaller, some antivirus programs (including Windows Defender SmartScreen) may flag it as unrecognized or potentially unsafe. 

**This is a false positive.** The application is completely safe and open-source—you can audit the full source code right here. 

* **How to run it:** If Windows SmartScreen blocks the launch, click on **"More info"** and then select **"Run anyway"**.
