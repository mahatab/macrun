"""Global hotkey via pynput (Cmd+Shift+R by default)."""

import threading
from pynput import keyboard


class HotkeyListener:
    """Listens for Cmd+Shift+R globally and calls a callback."""

    def __init__(self, callback):
        self._callback = callback
        self._listener = None
        self._pressed = set()

    def start(self):
        """Register global hotkey. Returns True on success."""
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.daemon = True
            self._listener.start()
            return True
        except Exception as e:
            print(f"[MacRun] Hotkey registration failed: {e}")
            return False

    def _on_press(self, key):
        self._pressed.add(key)
        # Check for Cmd+Shift+R
        if (keyboard.Key.cmd in self._pressed and
            keyboard.Key.shift in self._pressed and
            hasattr(key, 'char') and key.char and key.char.lower() == 'r'):
            # Dispatch to main thread
            self._dispatch_to_main()

    def _on_release(self, key):
        self._pressed.discard(key)

    def _dispatch_to_main(self):
        """Call the callback on the main thread via performSelector."""
        from Foundation import NSObject
        _HotkeyBridge.shared().triggerWithCallback_(self._callback)

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None


import objc
from Foundation import NSObject as _NSObject


class _HotkeyBridge(_NSObject):
    """Bridges hotkey events to the main thread."""

    _instance = None
    _pending_callback = None

    @classmethod
    def shared(cls):
        if cls._instance is None:
            cls._instance = cls.alloc().init()
        return cls._instance

    def triggerWithCallback_(self, callback):
        self._pending_callback = callback
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            b'fire:', None, False
        )

    def fire_(self, _):
        if self._pending_callback:
            self._pending_callback()
