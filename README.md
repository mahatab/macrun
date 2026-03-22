# MacRun

**Windows Run dialog (Win+R) for macOS.**

A lightweight menu bar app that brings the familiar Windows Run experience to your Mac. Press `Cmd+Shift+R` from anywhere to instantly launch apps, open files, browse URLs, or run shell commands.

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![macOS](https://img.shields.io/badge/macOS-13%2B-black.svg)
![Python](https://img.shields.io/badge/python-3.12-yellow.svg)

---

## Features

- **Global Hotkey** — `Cmd+Shift+R` opens the Run dialog from any app
- **Windows Command Translation** — Type `calc`, `notepad`, `taskmgr`, `cmd` and MacRun translates them to macOS equivalents with a helpful toast notification
- **105+ Built-in Aliases** — Windows commands, Control Panel applets (`.cpl`), MMC snap-ins (`.msc`), system tools, and networking commands all mapped
- **Smart Command Detection** — Automatically detects URLs, file paths, app names, and shell commands
- **Fuzzy App Search** — Type a partial app name and MacRun finds it via Spotlight
- **Command History** — Last 20 commands saved, with dropdown autocomplete
- **Browse Button** — Native file picker to select files or folders
- **Menu Bar Resident** — Lives quietly in your menu bar, no dock icon
- **Splash Screen** — Clean startup animation
- **Start at Login** — One-click toggle from the menu bar

## Screenshots

### Run Dialog
The dialog appears at the bottom-left of your screen, just like Windows:

- Type a command and press Enter
- Press Escape to dismiss
- Click Browse to pick a file

### Translation Toast
When you type a Windows command, MacRun shows what it translated to:

```
Translated: notepad → TextEdit
Translated: taskmgr → Activity Monitor
Translated: calc → Calculator
```

## Installation

### Prerequisites

- macOS 13+ (Ventura or later)
- Python 3.12 (via Homebrew)

### Setup

```bash
# Clone the repo
git clone https://github.com/mahatab/macrun.git
cd macrun

# Create virtual environment
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build the app
python setup.py py2app -A

# Install to Applications
ditto dist/MacRun.app /Applications/MacRun.app

# Launch
open /Applications/MacRun.app
```

### Permissions

On first launch, MacRun needs:

1. **Accessibility** — System Settings > Privacy & Security > Accessibility > Add MacRun
2. **Input Monitoring** — System Settings > Privacy & Security > Input Monitoring > Add MacRun

These are required for the global hotkey (`Cmd+Shift+R`) to work.

## Usage

### Hotkey

| Shortcut | Action |
|---|---|
| `Cmd+Shift+R` | Open/close the Run dialog |
| `Enter` | Execute command |
| `Escape` | Close dialog |
| `Browse...` | Open file picker |

### Command Examples

| You Type | What Happens |
|---|---|
| `calc` | Opens Calculator |
| `notepad` | Opens TextEdit |
| `cmd` | Opens Terminal |
| `taskmgr` | Opens Activity Monitor |
| `control` | Opens System Settings |
| `chrome` | Opens Google Chrome |
| `~/Downloads` | Opens Downloads in Finder |
| `google.com` | Opens in default browser |
| `wifi` | Opens Wi-Fi settings |
| `ls -la` | Runs shell command |

### Windows Command Mappings

MacRun includes 105+ mappings covering:

- **Apps** — `calc`, `notepad`, `cmd`, `explorer`, `chrome`, `code`, `slack`, `discord`, `spotify`, etc.
- **Control Panel** — `desk.cpl` (Display), `ncpa.cpl` (Network), `mmsys.cpl` (Sound), `firewall.cpl`, etc.
- **System Tools** — `taskmgr`, `msinfo32`, `diskmgmt.msc`, `devmgmt.msc`, `eventvwr.msc`, etc.
- **macOS Shortcuts** — `wifi`, `bluetooth`, `sound`, `display`, `battery`, `network`, `privacy`
- **Networking** — `ipconfig` → `ifconfig`, `tracert` → `traceroute`, etc.
- **File Paths** — `%USERPROFILE%` → `~`, `%APPDATA%` → `~/Library/Application Support`, etc.

When a Windows command is translated, a toast notification shows the macOS equivalent so you learn over time.

## Project Structure

```
macrun/
├── run.py                 # Entry point
├── setup.py               # py2app build config
├── requirements.txt       # Dependencies
├── LICENSE                 # MIT License
├── macrun/
│   ├── app.py             # Menu bar app (rumps)
│   ├── dialog.py          # Run dialog window (PyObjC/Cocoa)
│   ├── executor.py        # Command parsing & execution
│   ├── aliases.py         # 105+ Windows → macOS mappings
│   ├── history.py         # Command history (~/.macrun_history)
│   ├── hotkey.py          # Global hotkey (pynput)
│   ├── splash.py          # Startup splash screen
│   └── assets/
│       ├── run_icon.png   # App & dialog icon
│       ├── menubar_icon.png # Menu bar icon (template)
│       └── MacRun.icns    # macOS app icon
```

## Tech Stack

- **Python 3.12** with virtual environment
- **PyObjC** — Native Cocoa UI (NSWindow, NSComboBox, NSAlert)
- **rumps** — Menu bar integration
- **pynput** — Global hotkey listener
- **py2app** — macOS .app bundle packaging

## License

MIT License. See [LICENSE](LICENSE) for details.
