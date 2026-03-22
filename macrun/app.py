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
            None,  # separator
            rumps.MenuItem("Clear History", callback=self._clear_history),
            self._login_item,
            None,  # separator before Quit
        ]

    @rumps.clicked("Open Run Dialog  \u2318\u21E7R")
    def _open_dialog(self, sender=None):
        if self._dialog:
            self._dialog.show()

    @rumps.clicked("Clear History")
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
