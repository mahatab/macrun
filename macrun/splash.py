"""Splash screen shown briefly on app startup."""

import os
import objc
from AppKit import (
    NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSFloatingWindowLevel, NSScreen, NSMakeRect, NSColor, NSTextField,
    NSFont, NSImageView, NSImage, NSImageScaleProportionallyUpOrDown,
    NSGraphicsContext, NSBezierPath, NSObject, NSTimer, NSView,
    NSTextAlignmentCenter,
)


class SplashHelper(NSObject):
    """Timer target for auto-dismiss."""

    def init(self):
        self = objc.super(SplashHelper, self).init()
        if self is None:
            return None
        self._window = None
        self._callback = None
        return self

    def dismiss_(self, timer):
        if self._window:
            self._window.orderOut_(None)
            self._window = None
        if self._callback:
            self._callback()


def show_splash(on_dismiss=None, duration=2.0):
    """Show a splash screen. Calls on_dismiss when it closes."""
    screen = NSScreen.mainScreen()
    if not screen:
        if on_dismiss:
            on_dismiss()
        return

    sf = screen.frame()
    width, height = 320, 180
    x = sf.origin.x + (sf.size.width - width) / 2
    y = sf.origin.y + (sf.size.height - height) / 2

    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(x, y, width, height),
        NSWindowStyleMaskBorderless,
        NSBackingStoreBuffered,
        False,
    )
    window.setLevel_(NSFloatingWindowLevel + 2)
    window.setOpaque_(False)
    window.setBackgroundColor_(NSColor.clearColor())
    window.setHasShadow_(True)
    window.setReleasedWhenClosed_(False)

    # Rounded background view
    content = window.contentView()

    # Dark rounded rect background
    bg = _RoundedBackgroundView.alloc().initWithFrame_(
        NSMakeRect(0, 0, width, height)
    )
    content.addSubview_(bg)

    # App icon (larger, centered)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "run_icon.png")
    icon = NSImage.alloc().initWithContentsOfFile_(icon_path)
    if icon:
        icon_view = NSImageView.alloc().initWithFrame_(
            NSMakeRect((width - 64) / 2, 70, 64, 64)
        )
        icon_view.setImage_(icon)
        icon_view.setImageScaling_(NSImageScaleProportionallyUpOrDown)
        content.addSubview_(icon_view)

    # App name
    title = NSTextField.alloc().initWithFrame_(
        NSMakeRect(0, 40, width, 28)
    )
    title.setStringValue_("MacRun")
    title.setBezeled_(False)
    title.setDrawsBackground_(False)
    title.setEditable_(False)
    title.setSelectable_(False)
    title.setFont_(NSFont.boldSystemFontOfSize_(20))
    title.setTextColor_(NSColor.whiteColor())
    title.setAlignment_(NSTextAlignmentCenter)
    content.addSubview_(title)

    # Subtitle
    subtitle = NSTextField.alloc().initWithFrame_(
        NSMakeRect(0, 18, width, 18)
    )
    subtitle.setStringValue_("Windows Run for macOS")
    subtitle.setBezeled_(False)
    subtitle.setDrawsBackground_(False)
    subtitle.setEditable_(False)
    subtitle.setSelectable_(False)
    subtitle.setFont_(NSFont.systemFontOfSize_(12))
    subtitle.setTextColor_(NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.6))
    subtitle.setAlignment_(NSTextAlignmentCenter)
    content.addSubview_(subtitle)

    window.orderFrontRegardless()

    # Auto-dismiss
    helper = SplashHelper.alloc().init()
    helper._window = window
    helper._callback = on_dismiss
    # Keep references alive
    _splash_refs.append(helper)
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        duration, helper, b"dismiss:", None, False
    )

    return window


# prevent GC
_splash_refs = []


class _TimerHelper(NSObject):
    """Generic NSObject that fires a Python callback from an NSTimer."""

    def initWithCallback_(self, callback):
        self = objc.super(_TimerHelper, self).init()
        if self is None:
            return None
        self._callback = callback
        return self

    def fire_(self, timer):
        if self._callback:
            self._callback(timer)


class _RoundedBackgroundView(NSView):
    """Custom NSView that draws a dark rounded rectangle."""

    def drawRect_(self, rect):
        NSColor.colorWithCalibratedWhite_alpha_(0.12, 0.95).setFill()
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            self.bounds(), 16, 16
        )
        path.fill()
