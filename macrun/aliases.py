"""Windows-to-macOS command alias mappings."""

# Maps Windows commands (lowercase) to macOS equivalents.
# Value is either:
#   - str: the macOS command to execute
#   - tuple(str, str): (command, info message to display)
#   - None: no equivalent, show an error message

COMMAND_ALIASES = {
    # Common applications
    "calc": "open -a Calculator",
    "calculator": "open -a Calculator",
    "notepad": "open -a TextEdit",
    "cmd": "open -a Terminal",
    "cmd.exe": "open -a Terminal",
    "powershell": "open -a Terminal",
    "powershell.exe": "open -a Terminal",
    "explorer": "open -a Finder",
    "explorer.exe": "open -a Finder",
    "control": 'open "x-apple.systempreferences:"',
    "mspaint": "open -a Preview",
    "winword": "open -a 'Microsoft Word' || open -a Pages",
    "excel": "open -a 'Microsoft Excel' || open -a Numbers",
    "chrome": "open -a 'Google Chrome'",
    "firefox": "open -a Firefox",
    "safari": "open -a Safari",
    "code": "open -a 'Visual Studio Code'",
    "spotify": "open -a Spotify",
    "slack": "open -a Slack",
    "discord": "open -a Discord",
    "zoom": "open -a zoom.us",
    "iterm": "open -a iTerm",
    "warp": "open -a Warp",
    "photos": "open -a Photos",
    "music": "open -a Music",
    "mail": "open -a Mail",
    "messages": "open -a Messages",
    "facetime": "open -a FaceTime",
    "maps": "open -a Maps",
    "notes": "open -a Notes",
    "reminders": "open -a Reminders",
    "calendar": "open -a Calendar",
    "contacts": "open -a Contacts",
    "books": "open -a Books",
    "news": "open -a News",
    "stocks": "open -a Stocks",
    "weather": "open -a Weather",
    "clock": "open -a Clock",
    "wordpad": "open -a TextEdit",
    "write": "open -a TextEdit",

    # Control Panel applets (.cpl)
    "appwiz.cpl": ('open "x-apple.systempreferences:"',
                   "Use Finder > Applications to manage apps"),
    "desk.cpl": 'open "x-apple.systempreferences:com.apple.Displays-Settings.extension"',
    "ncpa.cpl": 'open "x-apple.systempreferences:com.apple.Network-Settings.extension"',
    "mmsys.cpl": 'open "x-apple.systempreferences:com.apple.Sound-Settings.extension"',
    "inetcpl.cpl": "open -a Safari",
    "firewall.cpl": 'open "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension"',
    "powercfg.cpl": 'open "x-apple.systempreferences:com.apple.Battery-Settings.extension"',
    "timedate.cpl": 'open "x-apple.systempreferences:com.apple.Date-Time-Settings.extension"',
    "intl.cpl": 'open "x-apple.systempreferences:com.apple.Localization-Settings.extension"',
    "joy.cpl": 'open "x-apple.systempreferences:com.apple.Game-Controller-Settings.extension"',
    "main.cpl": 'open "x-apple.systempreferences:com.apple.Mouse-Settings.extension"',

    # Microsoft Management Console (.msc)
    "devmgmt.msc": "open -a 'System Information'",
    "diskmgmt.msc": "open -a 'Disk Utility'",
    "services.msc": ("open -a Terminal",
                     "Use 'launchctl' in Terminal to manage services"),
    "compmgmt.msc": "open -a 'System Information'",
    "eventvwr.msc": "open -a Console",
    "taskschd.msc": (None, "Use crontab or launchd on macOS"),
    "lusrmgr.msc": 'open "x-apple.systempreferences:com.apple.Users-Groups-Settings.extension"',
    "certmgr.msc": "open -a 'Keychain Access'",
    "fsmgmt.msc": (None, "Use Sharing in System Settings"),

    # System tools
    "taskmgr": "open -a 'Activity Monitor'",
    "resmon": "open -a 'Activity Monitor'",
    "perfmon": "open -a 'Activity Monitor'",
    "msinfo32": "open -a 'System Information'",
    "dxdiag": "open -a 'System Information'",
    "cleanmgr": 'open "x-apple.systempreferences:com.apple.settings.Storage"',
    "dfrgui": (None, "macOS does not need defragmentation — APFS handles this automatically"),
    "snippingtool": ("screencapture -i ~/Desktop/screenshot.png",
                     "Use Cmd+Shift+5 for the native screenshot tool"),
    "magnify": 'open "x-apple.systempreferences:com.apple.Accessibility-Settings.extension"',
    "osk": (None, "Enable Keyboard Viewer in Input Sources menu bar"),
    "charmap": "open -a 'Font Book'",
    "mstsc": "open -a 'Microsoft Remote Desktop' || open -a 'Screen Sharing'",

    # Shutdown / session
    "shutdown /s": """osascript -e 'tell app "System Events" to shut down'""",
    "shutdown /r": """osascript -e 'tell app "System Events" to restart'""",
    "shutdown /l": """osascript -e 'tell app "System Events" to log out'""",
    "logoff": """osascript -e 'tell app "System Events" to log out'""",
    "rundll32 lockworkstation": "pmset displaysleepnow",

    # Networking (run in terminal)
    "ipconfig": ("ifconfig", "Translated: ipconfig → ifconfig"),
    "ipconfig /all": ("ifconfig -a", "Translated: ipconfig /all → ifconfig -a"),
    "ipconfig /flushdns": ("sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder",
                           "Flushing DNS cache"),
    "tracert": ("traceroute", "Translated: tracert → traceroute"),

    # File system / environment variables
    "explorer .": "open .",
    "explorer c:\\": "open /",
    "explorer %userprofile%": "open ~",
    "explorer %temp%": "open $TMPDIR",
    "explorer %appdata%": "open ~/Library/Application\\ Support",
    "%userprofile%": "open ~",
    "%homepath%": "open ~",

    # System preference shortcuts
    "wifi": 'open "x-apple.systempreferences:com.apple.wifi-settings-extension"',
    "bluetooth": 'open "x-apple.systempreferences:com.apple.BluetoothSettings"',
    "sound": 'open "x-apple.systempreferences:com.apple.Sound-Settings.extension"',
    "display": 'open "x-apple.systempreferences:com.apple.Displays-Settings.extension"',
    "battery": 'open "x-apple.systempreferences:com.apple.Battery-Settings.extension"',
    "network": 'open "x-apple.systempreferences:com.apple.Network-Settings.extension"',
    "privacy": 'open "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension"',

    # Other
    "winver": "sw_vers",
    "msedge": "open -a Safari",
    "outlook": "open -a 'Microsoft Outlook' || open -a Mail",
    "teams": "open -a 'Microsoft Teams'",
    "onenote": "open -a 'Microsoft OneNote'",
    "msiexec": (None, "Use 'brew install' or App Store on macOS"),
    "wt": "open -a Terminal",
    "wsl": (None, "WSL is Windows-only. macOS is already Unix-based — use Terminal directly"),

    # No macOS equivalent
    "msconfig": (None, "No direct equivalent on macOS. Use System Settings."),
    "regedit": (None, "macOS does not have a registry. Use defaults command or plist files."),
}

# Reverse lookup: build a display name for translations
ALIAS_DISPLAY_NAMES = {}
for key, val in COMMAND_ALIASES.items():
    if isinstance(val, str):
        # Extract app name from 'open -a "App Name"' or 'open -a AppName'
        if "open -a" in val:
            name = val.split("open -a")[-1].strip().strip("'\"")
            ALIAS_DISPLAY_NAMES[key] = name
