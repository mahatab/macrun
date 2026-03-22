"""Run dialog window — NSWindow with Cocoa UI elements."""

import objc
from AppKit import (
    NSWindow,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskClosable,
    NSFloatingWindowLevel,
    NSBackingStoreBuffered,
    NSMakeRect,
    NSTextField,
    NSComboBox,
    NSButton,
    NSBezelStyleRounded,
    NSImageView,
    NSImage,
    NSImageScaleProportionallyUpOrDown,
    NSFont,
    NSColor,
    NSBox,
    NSBoxSeparator,
    NSOpenPanel,
    NSAlert,
    NSAlertStyleWarning,
    NSAlertStyleInformational,
    NSApp,
    NSScreen,
    NSObject,
    NSTimer,
    NSWindowStyleMaskBorderless,
    NSLineBreakByWordWrapping,
    NSTextAlignmentLeft,
    NSTextAlignmentCenter,
)
from Foundation import NSSize

from macrun import history, executor


# --- Combo Box Data Source ---

class ComboBoxDataSource(NSObject):
    """Provides history items to the NSComboBox."""

    def init(self):
        self = objc.super(ComboBoxDataSource, self).init()
        if self is None:
            return None
        self._items = []
        return self

    def setItems_(self, items):
        self._items = list(items)

    def numberOfItemsInComboBox_(self, combo):
        return len(self._items)

    def comboBox_objectValueForItemAtIndex_(self, combo, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return ""

    def comboBox_completedString_(self, combo, partial):
        partial_lower = partial.lower()
        for item in self._items:
            if item.lower().startswith(partial_lower):
                return item
        return None

    def comboBox_indexOfItemWithStringValue_(self, combo, string):
        try:
            return self._items.index(string)
        except ValueError:
            from AppKit import NSNotFound
            return NSNotFound


# --- Toast Helper (NSObject subclass for timer target) ---

class ToastHelper(NSObject):
    """NSObject subclass that can be a timer target for toast dismiss."""

    def init(self):
        self = objc.super(ToastHelper, self).init()
        if self is None:
            return None
        self._window = None
        return self

    def setWindow_(self, window):
        self._window = window

    def dismiss_(self, timer):
        if self._window:
            self._window.orderOut_(None)
            self._window = None


# Toast references to prevent GC
_active_toasts = []


def show_toast(message, duration=2.5):
    """Show a toast message near the bottom of the screen."""
    screen = NSScreen.mainScreen()
    if not screen:
        return
    screen_frame = screen.visibleFrame()

    width = 420
    height = 36
    x = screen_frame.origin.x + (screen_frame.size.width - width) / 2
    y = screen_frame.origin.y + 60

    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(x, y, width, height),
        NSWindowStyleMaskBorderless,
        NSBackingStoreBuffered,
        False,
    )
    window.setLevel_(NSFloatingWindowLevel + 1)
    window.setOpaque_(False)
    window.setBackgroundColor_(NSColor.colorWithCalibratedWhite_alpha_(0.15, 0.92))
    window.setHasShadow_(True)
    window.setReleasedWhenClosed_(False)

    label = NSTextField.alloc().initWithFrame_(NSMakeRect(16, 4, width - 32, 28))
    label.setStringValue_(message)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setEditable_(False)
    label.setSelectable_(False)
    label.setFont_(NSFont.systemFontOfSize_(13))
    label.setTextColor_(NSColor.whiteColor())
    label.setAlignment_(NSTextAlignmentCenter)
    window.contentView().addSubview_(label)

    window.orderFrontRegardless()

    helper = ToastHelper.alloc().init()
    helper.setWindow_(window)
    _active_toasts.append((window, helper))
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        duration, helper, b"dismiss:", None, False
    )


def show_output_window(title, output_text):
    """Show command output in a scrollable window."""
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(output_text[:2000])
    alert.setAlertStyle_(NSAlertStyleInformational)
    alert.addButtonWithTitle_("OK")
    alert.runModal()


def show_error(message):
    """Show a macOS-style error alert."""
    alert = NSAlert.alloc().init()
    alert.setMessageText_("Error")
    alert.setInformativeText_(message)
    alert.setAlertStyle_(NSAlertStyleWarning)
    alert.addButtonWithTitle_("OK")
    alert.runModal()


# --- Dialog Controller (NSObject subclass for button targets) ---

class DialogController(NSObject):
    """NSObject subclass that handles button actions for the Run dialog."""

    def init(self):
        self = objc.super(DialogController, self).init()
        if self is None:
            return None
        self._window = None
        self._combo = None
        self._data_source = None
        return self

    def setWindow_(self, window):
        self._window = window

    def setCombo_(self, combo):
        self._combo = combo

    def setDataSource_(self, ds):
        self._data_source = ds

    def okClicked_(self, sender):
        command = self._combo.stringValue().strip()
        if not command:
            self._window.orderOut_(None)
            return

        history.add_to_history(command)
        self._window.orderOut_(None)

        result = executor.execute(command)

        if result.output:
            title = result.translated_to or command
            show_output_window(title, result.output)
        elif result.translated_from and result.translated_to:
            show_toast(f"Translated: {result.translated_from} \u2192 {result.translated_to}")
        elif result.info_message and not result.success:
            show_error(result.info_message)
        elif not result.success:
            msg = result.message or (
                f"macOS cannot find '{command}'. Make sure you typed the "
                f"name correctly, and then try again."
            )
            show_error(msg)

    def cancelClicked_(self, sender):
        self._window.orderOut_(None)

    def browseClicked_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(True)
        panel.setAllowsMultipleSelection_(False)

        if panel.runModal() == 1:  # NSOKButton
            url = panel.URLs()[0]
            self._combo.setStringValue_(url.path())


# --- Main Run Dialog ---

class RunDialog:
    """The Run dialog window — replicates Windows 11 Run dialog."""

    WINDOW_WIDTH = 430
    CONTENT_HEIGHT = 180  # content area only (title bar is extra)

    def __init__(self):
        self._window = None
        self._combo = None
        self._data_source = None
        self._controller = None
        self._build()

    def _build(self):
        """Construct the NSWindow and all UI elements."""
        W = self.WINDOW_WIDTH
        H = self.CONTENT_HEIGHT

        # Position: bottom-left of screen (like Windows Run dialog)
        screen = NSScreen.mainScreen()
        if screen:
            sf = screen.visibleFrame()
            x = sf.origin.x + 10
            y = sf.origin.y + 10
        else:
            x, y = 50, 50

        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, W, H),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False,
        )
        self._window.setTitle_("Run")
        self._window.setLevel_(NSFloatingWindowLevel)
        self._window.setReleasedWhenClosed_(False)
        self._window.setIsVisible_(False)

        content = self._window.contentView()

        # --- Controller ---
        self._controller = DialogController.alloc().init()
        self._controller.setWindow_(self._window)

        # ============================================================
        # LAYOUT — Cocoa y=0 is BOTTOM. We lay out from top to bottom.
        # Content area is H pixels tall.
        # ============================================================

        # --- Row 1: Icon + instruction text (top area) ---
        # Icon: 32x32, positioned at top-left with padding
        icon_y = H - 16 - 32  # 16px top padding, 32px icon height
        icon_view = NSImageView.alloc().initWithFrame_(
            NSMakeRect(16, icon_y, 32, 32)
        )
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "run_icon.png")
        icon = NSImage.alloc().initWithContentsOfFile_(icon_path)
        if icon:
            icon_view.setImage_(icon)
            icon_view.setImageScaling_(NSImageScaleProportionallyUpOrDown)
        content.addSubview_(icon_view)

        # Instruction text: right of icon, wrapping
        text_x = 58
        text_w = W - text_x - 16
        text_y = H - 16 - 42  # slightly lower than icon to vertically center
        instruction = NSTextField.alloc().initWithFrame_(
            NSMakeRect(text_x, text_y, text_w, 42)
        )
        instruction.setStringValue_(
            "Type the name of a program, folder, document, or "
            "Internet resource, and macOS will open it for you."
        )
        instruction.setBezeled_(False)
        instruction.setDrawsBackground_(False)
        instruction.setEditable_(False)
        instruction.setSelectable_(False)
        instruction.setFont_(NSFont.systemFontOfSize_(12))
        instruction.setTextColor_(NSColor.secondaryLabelColor())
        instruction.setLineBreakMode_(NSLineBreakByWordWrapping)
        instruction.setCell_(instruction.cell())
        instruction.cell().setWraps_(True)
        content.addSubview_(instruction)

        # --- Row 2: "Open:" label + ComboBox (middle area) ---
        row2_y = H - 78  # below the instruction text
        open_label = NSTextField.alloc().initWithFrame_(
            NSMakeRect(16, row2_y, 38, 20)
        )
        open_label.setStringValue_("Open:")
        open_label.setBezeled_(False)
        open_label.setDrawsBackground_(False)
        open_label.setEditable_(False)
        open_label.setSelectable_(False)
        open_label.setFont_(NSFont.boldSystemFontOfSize_(12))
        open_label.setTextColor_(NSColor.labelColor())
        content.addSubview_(open_label)

        combo_x = 58
        self._combo = NSComboBox.alloc().initWithFrame_(
            NSMakeRect(combo_x, row2_y - 2, W - combo_x - 16, 26)
        )
        self._combo.setFont_(NSFont.systemFontOfSize_(13))
        self._combo.setCompletes_(True)
        self._combo.setNumberOfVisibleItems_(10)
        self._combo.setUsesDataSource_(True)

        self._data_source = ComboBoxDataSource.alloc().init()
        self._combo.setDataSource_(self._data_source)
        self._controller.setCombo_(self._combo)
        self._controller.setDataSource_(self._data_source)
        content.addSubview_(self._combo)

        # --- Divider line ---
        divider_y = H - 110
        divider = NSBox.alloc().initWithFrame_(
            NSMakeRect(0, divider_y, W, 1)
        )
        divider.setBoxType_(NSBoxSeparator)
        content.addSubview_(divider)

        # --- Row 3: Buttons (bottom area) ---
        btn_y = divider_y - 38  # buttons below divider
        btn_h = 28

        # Browse... button (left side)
        browse_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(16, btn_y, 85, btn_h)
        )
        browse_btn.setTitle_("Browse...")
        browse_btn.setBezelStyle_(NSBezelStyleRounded)
        browse_btn.setTarget_(self._controller)
        browse_btn.setAction_(b"browseClicked:")
        content.addSubview_(browse_btn)

        # OK button (rightmost)
        ok_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(W - 16 - 75, btn_y, 75, btn_h)
        )
        ok_btn.setTitle_("OK")
        ok_btn.setBezelStyle_(NSBezelStyleRounded)
        ok_btn.setKeyEquivalent_("\r")
        ok_btn.setTarget_(self._controller)
        ok_btn.setAction_(b"okClicked:")
        content.addSubview_(ok_btn)

        # Cancel button (left of OK)
        cancel_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(W - 16 - 75 - 8 - 75, btn_y, 75, btn_h)
        )
        cancel_btn.setTitle_("Cancel")
        cancel_btn.setBezelStyle_(NSBezelStyleRounded)
        cancel_btn.setKeyEquivalent_(chr(27))
        cancel_btn.setTarget_(self._controller)
        cancel_btn.setAction_(b"cancelClicked:")
        content.addSubview_(cancel_btn)

    def show(self):
        """Show the dialog, populating combo box with latest history."""
        items = history.load_history()
        self._data_source.setItems_(items)
        self._combo.reloadData()
        self._combo.setStringValue_("")

        # Position: bottom-left of screen (like Windows)
        screen = NSScreen.mainScreen()
        if screen:
            sf = screen.visibleFrame()
            x = sf.origin.x + 10
            y = sf.origin.y + 10
            self._window.setFrameOrigin_((x, y))

        self._window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        self._window.makeFirstResponder_(self._combo)

    def hide(self):
        self._window.orderOut_(None)

    def is_visible(self):
        return self._window.isVisible()
