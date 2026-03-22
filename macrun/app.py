"""Main application — rumps-based menu bar app + PyObjC dialog."""

import os
import subprocess
import rumps

from macrun import history

LAUNCH_AGENT_LABEL = "com.macrun.app"
LAUNCH_AGENT_PATH = os.path.expanduser(f"~/Library/LaunchAgents/{LAUNCH_AGENT_LABEL}.plist")
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLIST_SOURCE = os.path.join(PROJECT_DIR, f"{LAUNCH_AGENT_LABEL}.plist")


class MacRunApp(rumps.App):
    def __init__(self):
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "menubar_icon.png")
        super().__init__("MacRun", icon=icon_path, template=True)
        self._dialog = None
        self._hotkey = None

        # Build menu
        self._login_item = rumps.MenuItem(
            "Start at Login",
            callback=self._toggle_login,
        )
        self._login_item.state = os.path.exists(LAUNCH_AGENT_PATH)

        self.menu = [
            rumps.MenuItem("Open Run Dialog  \u2318\u21E7R", callback=self._open_dialog),
            None,
            self._login_item,
            rumps.MenuItem("Clear History", callback=self._clear_history),
            rumps.MenuItem("Command Aliases", callback=self._show_aliases),
            None,
        ]

    def _open_dialog(self, sender=None):
        if self._dialog:
            self._dialog.show()

    def _show_aliases(self, _=None):
        try:
            from macrun.aliases import COMMAND_ALIASES

            # Categorize aliases
            categories = {
                "Applications": [],
                "Control Panel (.cpl)": [],
                "System Tools (.msc)": [],
                "System Utilities": [],
                "macOS Settings Shortcuts": [],
                "Networking": [],
                "File System & Paths": [],
                "Shutdown & Session": [],
                "No macOS Equivalent": [],
            }

            settings_keys = {"wifi", "bluetooth", "sound", "display", "battery", "network", "privacy"}
            net_keys = {"ipconfig", "ipconfig /all", "ipconfig /flushdns", "tracert"}
            path_keys = {"explorer .", "explorer c:\\", "explorer %userprofile%", "explorer %temp%",
                         "explorer %appdata%", "%userprofile%", "%homepath%"}
            shutdown_keys = {"shutdown /s", "shutdown /r", "shutdown /l", "logoff", "rundll32 lockworkstation"}
            util_keys = {"taskmgr", "resmon", "perfmon", "msinfo32", "dxdiag", "cleanmgr", "dfrgui",
                         "snippingtool", "magnify", "osk", "charmap", "mstsc", "winver"}

            for key in sorted(COMMAND_ALIASES.keys()):
                val = COMMAND_ALIASES[key]
                if isinstance(val, tuple):
                    cmd, msg = val
                    if cmd is None:
                        mac = '<span class="no-equiv">' + msg + '</span>'
                    else:
                        mac = cmd + ' <span class="hint">(' + msg + ')</span>'
                else:
                    mac = val

                row = "<tr><td><code>" + key + "</code></td><td>" + mac + "</td></tr>"

                if isinstance(val, tuple) and val[0] is None:
                    categories["No macOS Equivalent"].append(row)
                elif key in settings_keys:
                    categories["macOS Settings Shortcuts"].append(row)
                elif key in net_keys:
                    categories["Networking"].append(row)
                elif key in path_keys:
                    categories["File System & Paths"].append(row)
                elif key in shutdown_keys:
                    categories["Shutdown & Session"].append(row)
                elif key in util_keys:
                    categories["System Utilities"].append(row)
                elif key.endswith(".cpl"):
                    categories["Control Panel (.cpl)"].append(row)
                elif key.endswith(".msc"):
                    categories["System Tools (.msc)"].append(row)
                else:
                    categories["Applications"].append(row)

            # Build HTML sections
            sections = []
            for cat, rows in categories.items():
                if not rows:
                    continue
                sections.append(
                    '<h2>' + cat + ' <span class="count">(' + str(len(rows)) + ')</span></h2>\n'
                    '<table><tr><th>Windows Command</th><th>macOS Action</th></tr>\n'
                    + "\n".join(rows) +
                    '\n</table>'
                )

            html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MacRun Command Aliases</title>
<style>
body{font-family:-apple-system,sans-serif;margin:40px auto;max-width:750px;color:#e0e0e0;background:#1e1e1e;padding:0 20px}
h1{font-size:24px;margin-bottom:4px}
h2{font-size:16px;margin-top:32px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #333}
.count{color:#888;font-weight:normal;font-size:13px}
.subtitle{color:#999;font-size:14px}
table{width:100%;border-collapse:collapse;margin-top:8px}
th{text-align:left;padding:8px 12px;background:#2a2a2a;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px}
td{padding:7px 12px;border-bottom:1px solid #2a2a2a;font-size:13px}
tr:hover{background:#252525}
code{background:#333;padding:2px 6px;border-radius:4px;font-size:12px;color:#6cb6ff}
.no-equiv{color:#e06050;font-style:italic}
.hint{color:#888;font-size:12px}
nav{margin:16px 0;padding:12px;background:#252525;border-radius:8px;font-size:13px;line-height:2}
nav a{color:#6cb6ff;text-decoration:none;margin-right:16px}
nav a:hover{text-decoration:underline}
@media(prefers-color-scheme:light){
body{background:#fff;color:#222}
h2{border-bottom:1px solid #e0e0e0}
th{background:#f5f5f5;color:#444}
td{border-bottom:1px solid #eee}
tr:hover{background:#f8f8f8}
code{background:#f0f0f0;color:#0550ae}
nav{background:#f5f5f5}
nav a{color:#0550ae}
.subtitle{color:#666}
.no-equiv{color:#d03030}
.hint{color:#888}
}
</style></head><body>
<h1>MacRun Command Aliases</h1>
<p class="subtitle">""" + str(len(COMMAND_ALIASES)) + """ Windows commands mapped to macOS equivalents</p>
<nav>""" + " ".join(
                '<a href="#' + cat.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "") + '">' + cat + '</a>'
                for cat in categories if categories[cat]
            ) + """</nav>
""" + "\n".join(
                s.replace('<h2>', '<h2 id="' + list(categories.keys())[i].lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "") + '">')
                for i, s in enumerate(sections)
            ) + """
</body></html>"""

            path = os.path.expanduser("~/.macrun_aliases.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            os.system('open "' + path + '"')
        except Exception as e:
            rumps.alert("Error", str(e))

    def _clear_history(self, sender=None):
        history.clear_history()

    def _on_hotkey(self):
        if self._dialog:
            if self._dialog.is_visible():
                self._dialog.hide()
            else:
                self._dialog.show()

    def _toggle_login(self, sender):
        if os.path.exists(LAUNCH_AGENT_PATH):
            subprocess.run(["launchctl", "unload", LAUNCH_AGENT_PATH],
                           capture_output=True)
            try:
                os.remove(LAUNCH_AGENT_PATH)
            except OSError:
                pass
            sender.state = False
        else:
            os.makedirs(os.path.dirname(LAUNCH_AGENT_PATH), exist_ok=True)
            if os.path.exists(PLIST_SOURCE):
                import shutil
                shutil.copy2(PLIST_SOURCE, LAUNCH_AGENT_PATH)
                subprocess.run(["launchctl", "load", LAUNCH_AGENT_PATH],
                               capture_output=True)
                sender.state = True


def main():
    app = MacRunApp()

    from macrun.splash import show_splash
    from macrun.dialog import RunDialog
    from macrun.hotkey import HotkeyListener

    app._splash = show_splash(duration=2.5)
    app._dialog = RunDialog()

    app._hotkey = HotkeyListener(app._on_hotkey)
    if not app._hotkey.start():
        rumps.alert(
            title="Accessibility Permission Required",
            message=(
                "MacRun needs Accessibility permission for the global hotkey "
                "(Cmd+Shift+R).\n\n"
                "Go to System Settings > Privacy & Security > Accessibility "
                "and add MacRun.\n\n"
                "You can still use MacRun from the menu bar icon."
            ),
        )

    app.run()
