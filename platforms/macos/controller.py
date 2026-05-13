from __future__ import annotations
import threading
from pathlib import Path

import objc
from AppKit import (
    NSApp, NSApplication, NSColor, NSEvent, NSEventModifierFlagCommand,
    NSFloatingWindowLevel,
    NSMenu, NSMenuItem, NSScreen, NSStatusBar, NSStatusWindowLevel,
    NSVariableStatusItemLength, NSWindow,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorIgnoresCycle,
    NSWindowCollectionBehaviorStationary,
    NSWindowStyleMaskBorderless, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSWindowStyleMaskTitled, NSBackingStoreBuffered, NSWorkspace,
)
from Foundation import NSMakeRect, NSObject, NSTimer, NSURL, NSURLRequest
from WebKit import WKWebView, WKWebViewConfiguration

from core.models.app_config import PORT
from core.viewmodels.app_viewmodel import AppViewModel

try:
    from AppKit import NSScreenSaverWindowLevel as _SSL
    BREAK_WINDOW_LEVEL = _SSL
except ImportError:
    BREAK_WINDOW_LEVEL = 101  # NSPopUpMenuWindowLevel — accepts key input in WKWebView

_MI: dict[str, dict] = {
    "zh": {
        "app_title":    "re.set  休息提醒",
        "timer_fmt":    lambda m, s: f"下次休息：{m:02d}:{s:02d}",
        "snooze_fmt":   lambda m, s: f"已推迟：{m:02d}:{s:02d}",
        "pause":        "暂停计时",
        "resume_log":   "回来了，记录一下",
        "away_form":    "记录工作时段",
        "trigger":      "立即触发休息",
        "plan_today":   "规划今天",
        "records":      "查看今日记录",
        "prefs":        "设置",
        "eod_on":       "下班了",
        "eod_off":      "恢复提醒",
        "quit":         "退出",
    },
    "en": {
        "app_title":    "re.set  Break Reminder",
        "timer_fmt":    lambda m, s: f"Next break: {m:02d}:{s:02d}",
        "snooze_fmt":   lambda m, s: f"Snoozed: {m:02d}:{s:02d}",
        "pause":        "Pause Timer",
        "resume_log":   "I'm back — log it",
        "away_form":    "Log Work Session",
        "trigger":      "Trigger Break Now",
        "plan_today":   "Plan Today",
        "records":      "View Today's Records",
        "prefs":        "Preferences",
        "eod_on":       "End of Day",
        "eod_off":      "Resume Breaks",
        "quit":         "Quit",
    },
}


class _BreakWindow(NSWindow):
    """Borderless NSWindow that accepts key/main window status for WKWebView input."""
    def canBecomeKeyWindow(self):  return True
    def canBecomeMainWindow(self): return True


class MacOSController(NSObject):
    """
    NSObject subclass that acts as AppDelegate + owns all windows and the
    status bar.  Pure display layer — all state lives in AppViewModel.
    """

    def initWithAppViewModel_resourceDir_(self, app_vm: AppViewModel, resource_dir: Path):
        self = objc.super(MacOSController, self).init()
        if self is None:
            return None
        self._app_vm       = app_vm
        self._resource_dir = resource_dir
        self._bw      = None   # primary break window
        self._bwv     = None   # WKWebView in primary break window
        self._bw_extra: list = []
        self._ww      = None   # warning panel
        self._rw      = None   # records window
        self._waw     = None   # away-form / return-form window
        self._wp      = None   # preferences window
        self._si      = None   # NSStatusItem
        self._si_timer    = None
        self._si_pause    = None
        self._si_eod      = None
        self._si_hdr      = None
        self._si_away_form = None
        self._si_trig     = None
        self._si_plan     = None
        self._si_rec      = None
        self._si_prefs    = None
        self._pw      = None   # plan-today window
        self._key_monitor = None
        return self

    # ── AppDelegate ───────────────────────────────────────────────────────────

    def applicationDidFinishLaunching_(self, _):
        self._setup_status_bar()
        self._setup_subscriptions()
        self._setup_key_monitor()
        ws_nc = NSWorkspace.sharedWorkspace().notificationCenter()
        ws_nc.addObserver_selector_name_object_(
            self, "screenDidWake:", "NSWorkspaceScreensDidWakeNotification", None)

    def applicationShouldTerminateAfterLastWindowClosed_(self, _):
        return False

    @objc.python_method
    def _setup_subscriptions(self) -> None:
        """Wire AppViewModel observables to platform UI (called once after app launch)."""
        url = f"http://localhost:{PORT}/"

        def on_break(show: bool) -> None:
            if show:
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    "showBreakWindow:", url, False)

        def on_warning(show: bool) -> None:
            sel = "showWarningPanel:" if show else "hideWarningPanel:"
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                sel, None, False)

        self._app_vm.show_break_window.subscribe(on_break)
        self._app_vm.show_warning_panel.subscribe(on_warning)

    @objc.python_method
    def _setup_key_monitor(self) -> None:
        """Intercept Cmd+Esc to force-close the break window (emergency exit)."""
        NSEventMaskKeyDown = 1 << 10

        def handler(event):
            if (event.keyCode() == 53 and  # Escape
                    bool(event.modifierFlags() & NSEventModifierFlagCommand)):
                if self._bw and self._bw.isVisible():
                    self._app_vm.release_break_lock(reset_active=True)
                    self._app_vm.hide_break_window()
                    self.performSelectorOnMainThread_withObject_waitUntilDone_(
                        "hideBreakWindow:", None, False)
                    return None  # consume the event
            return event

        self._key_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskKeyDown, handler)

    # ── Status bar setup ──────────────────────────────────────────────────────

    @objc.python_method
    def _L(self, key: str):
        lang = self._app_vm.lang
        return _MI.get(lang, _MI["zh"]).get(key, key)

    @objc.python_method
    def _setup_status_bar(self):
        from AppKit import NSImage
        bar      = NSStatusBar.systemStatusBar()
        self._si = bar.statusItemWithLength_(NSVariableStatusItemLength)
        btn = self._si.button()
        if btn is not None:
            try:
                img = NSImage.imageWithSystemSymbolName_accessibilityDescription_(
                    "leaf.fill", "re.set")
                if img:
                    img.setTemplate_(True)
                    btn.setImage_(img)
                else:
                    btn.setTitle_("🌿")
            except Exception:
                btn.setTitle_("🌿")
        else:
            self._si.setTitle_("🌿")

        menu = NSMenu.alloc().init()

        def _item(title, action, key="", enabled=True, target=None):
            it = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, key)
            if not enabled:
                it.setEnabled_(False)
            if target:
                it.setTarget_(target)
            menu.addItem_(it)
            return it

        self._si_hdr   = _item(self._L("app_title"), None, enabled=False)
        self._si_timer = _item("—", None, enabled=False)
        menu.addItem_(NSMenuItem.separatorItem())
        self._si_pause     = _item(self._L("pause"),     "handlePause:",     target=self)
        self._si_away_form = _item(self._L("away_form"), "handleAwayForm:",  target=self)
        self._si_trig      = _item(self._L("trigger"),   "handleTrigger:",   target=self)
        menu.addItem_(NSMenuItem.separatorItem())
        self._si_plan  = _item(self._L("plan_today"), "handlePlanToday:", target=self)
        self._si_rec   = _item(self._L("records"), "handleViewRecords:", target=self)
        self._si_prefs = _item(self._L("prefs"),   "handlePreferences:", target=self)
        menu.addItem_(NSMenuItem.separatorItem())
        self._si_eod = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            self._eod_title(), "handleEndOfDay:", "")
        self._si_eod.setTarget_(self)
        menu.addItem_(self._si_eod)
        menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            self._L("quit"), "terminate:", "q")
        quit_item.setTarget_(NSApp)
        menu.addItem_(quit_item)

        self._si.setMenu_(menu)
        self._apply_menu_visibility()
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            5.0, self, "updateStatusBar:", None, True)

    # ── Menu helpers ──────────────────────────────────────────────────────────

    @objc.python_method
    def _eod_title(self) -> str:
        return self._L("eod_off") if self._app_vm.is_end_of_day.value else self._L("eod_on")

    @objc.python_method
    def _pause_title(self) -> str:
        if self._app_vm.is_away_mode.value:
            secs = self._app_vm._timer.away_elapsed_seconds
            m, s = secs // 60, secs % 60
            return self._L("resume_log") + f"  ({m:02d}:{s:02d})"
        return self._L("pause")

    @objc.python_method
    def _apply_menu_visibility(self) -> None:
        cfg = self._app_vm.config
        pairs = [
            (self._si_pause,     "away_tracking"),
            (self._si_away_form, "away_tracking"),
            (self._si_trig,      "trigger_break"),
            (self._si_plan,      "plan_today"),
            (self._si_rec,       "view_records"),
            (self._si_eod,       "end_of_day"),
        ]
        for item, key in pairs:
            if item:
                item.setHidden_(not cfg.feature_enabled(key))

    def updateMenuAfterPrefs_(self, _):
        """Called on main thread after preferences saved via HTTP."""
        if self._si_hdr:       self._si_hdr.setTitle_(self._L("app_title"))
        if self._si_pause:     self._si_pause.setTitle_(self._pause_title())
        if self._si_away_form: self._si_away_form.setTitle_(self._L("away_form"))
        if self._si_trig:      self._si_trig.setTitle_(self._L("trigger"))
        if self._si_plan:      self._si_plan.setTitle_(self._L("plan_today"))
        if self._si_rec:       self._si_rec.setTitle_(self._L("records"))
        if self._si_prefs:     self._si_prefs.setTitle_(self._L("prefs"))
        if self._si_eod:       self._si_eod.setTitle_(self._eod_title())
        self._apply_menu_visibility()
        # Reload visible records window so it picks up the new language
        if self._rw and self._rw.isVisible():
            self._rw.contentView().loadRequest_(
                NSURLRequest.requestWithURL_(
                    NSURL.URLWithString_(f"http://localhost:{PORT}/records")))

    def updateStatusBar_(self, _timer):
        text = self._app_vm.timer_display_text.value
        if self._si_timer:
            self._si_timer.setTitle_(text)
        if self._si_pause:
            self._si_pause.setTitle_(self._pause_title())
        if self._si_eod:
            self._si_eod.setTitle_(self._eod_title())

    # ── Menu actions ──────────────────────────────────────────────────────────

    def screenDidWake_(self, _):
        if self._app_vm.is_away_mode.value:
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showReturnForm:", None, False)

    def handlePause_(self, _):
        if self._app_vm.is_away_mode.value:
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showReturnForm:", None, False)
        else:
            threading.Thread(target=self._app_vm.pause_timer, daemon=True).start()
            url = f"http://localhost:{PORT}/?away=1"
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showBreakWindow:", url, False)

    def handleAwayForm_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showAwayForm:", None, False)

    def handleTrigger_(self, _):
        threading.Thread(target=self._app_vm.trigger_break_now, daemon=True).start()

    def handleViewRecords_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showRecordsPanel:", None, False)

    def handlePlanToday_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showPlanWindow:", None, False)

    def handlePreferences_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showPreferences:", None, False)

    def handleEndOfDay_(self, _):
        threading.Thread(
            target=lambda: (
                self._app_vm.toggle_end_of_day(),
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    "updateMenuAfterPrefs:", None, False),
            ),
            daemon=True,
        ).start()

    # ── Window helpers ────────────────────────────────────────────────────────

    @objc.python_method
    def _wkview(self, frame):
        cfg = WKWebViewConfiguration.alloc().init()
        return WKWebView.alloc().initWithFrame_configuration_(frame, cfg)

    @objc.python_method
    def _load_url(self, wkview, path: str) -> None:
        wkview.loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}{path}")))

    # ── Break window ──────────────────────────────────────────────────────────

    @objc.python_method
    def _make_break_window(self, frame):
        bw = _BreakWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
        bw.setLevel_(BREAK_WINDOW_LEVEL)
        bw.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorIgnoresCycle)
        bw.setDelegate_(self)
        bw.setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(
            0.969, 0.969, 0.976, 1.0))
        bwv = self._wkview(frame)
        bw.setContentView_(bwv)
        return bw, bwv

    @objc.python_method
    def _make_cover_window(self, frame) -> NSWindow:
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
        win.setLevel_(BREAK_WINDOW_LEVEL)
        win.setBackgroundColor_(NSColor.blackColor())
        win.setOpaque_(True)
        win.setReleasedWhenClosed_(False)
        win.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary)
        return win

    def showBreakWindow_(self, url_str: str):
        frame = NSScreen.mainScreen().frame()
        if not self._bw:
            self._bw, self._bwv = self._make_break_window(frame)
        else:
            self._bw.setFrame_display_(frame, False)
        req = NSURLRequest.requestWithURL_(NSURL.URLWithString_(url_str))
        self._bwv.loadRequest_(req)
        self._bw.makeKeyAndOrderFront_(None)
        self._bw.makeFirstResponder_(self._bwv)
        NSApp.activateIgnoringOtherApps_(True)
        # Cover additional screens
        screens = list(NSScreen.screens() or [])
        main_fr = NSScreen.mainScreen().frame()
        for bw in self._bw_extra:
            bw.orderOut_(None)
        self._bw_extra = []
        for scr in screens:
            fr = scr.frame()
            if (abs(fr.origin.x - main_fr.origin.x) < 1 and
                    abs(fr.origin.y - main_fr.origin.y) < 1):
                continue
            cover = self._make_cover_window(fr)
            cover.makeKeyAndOrderFront_(None)
            self._bw_extra.append(cover)

    def hideBreakWindow_(self, _):
        if self._bw:
            self._bw.orderOut_(None)
        for bw in self._bw_extra:
            bw.orderOut_(None)
        self._bw_extra = []

    def windowShouldClose_(self, _):
        return False

    # ── Warning panel ─────────────────────────────────────────────────────────

    def showWarningPanel_(self, _):
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pw, ph = 380.0, 114.0
        pf = NSMakeRect(sw - pw - 20, sh - ph - 20, pw, ph)
        if not self._ww:
            self._ww = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
            self._ww.setLevel_(NSStatusWindowLevel + 1)
            self._ww.setOpaque_(False)
            self._ww.setBackgroundColor_(NSColor.clearColor())
            self._ww.setHasShadow_(True)
            self._ww.setCollectionBehavior_(
                NSWindowCollectionBehaviorCanJoinAllSpaces
                | NSWindowCollectionBehaviorStationary)
            self._ww.setContentView_(self._wkview(NSMakeRect(0, 0, pw, ph)))
        self._ww.setFrame_display_(pf, False)
        self._load_url(self._ww.contentView(), "/warning")
        self._ww.orderFront_(None)

    def hideWarningPanel_(self, _):
        if self._ww:
            self._ww.orderOut_(None)

    # ── Auxiliary popup (away-form / return-form) ─────────────────────────────

    @objc.python_method
    def _make_aux_window(self, w: float, h: float) -> NSWindow:
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pf = NSMakeRect((sw - w) / 2, (sh - h) / 2, w, h)
        mask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            pf, mask, NSBackingStoreBuffered, False)
        win.setReleasedWhenClosed_(False)
        win.setLevel_(NSFloatingWindowLevel)
        win.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
        win.setContentView_(self._wkview(NSMakeRect(0, 0, w, h)))
        return win

    def showReturnForm_(self, _):
        if not self._waw:
            self._waw = self._make_aux_window(420.0, 540.0)
        lang = self._app_vm.lang
        title = "re.set — 回来啦" if lang == "zh" else "re.set — Welcome Back"
        self._waw.setTitle_(title)
        self._load_url(self._waw.contentView(), "/return-form")
        self._waw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def showAwayForm_(self, _):
        if not self._waw:
            self._waw = self._make_aux_window(420.0, 340.0)
        lang = self._app_vm.lang
        title = "re.set — 记录工作时段" if lang == "zh" else "re.set — Log Work Session"
        self._waw.setTitle_(title)
        self._load_url(self._waw.contentView(), "/away-form")
        self._waw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def closeAuxWindow_(self, _):
        if self._waw:
            self._waw.orderOut_(None)
        if self._pw:
            self._pw.orderOut_(None)

    # ── Records window ────────────────────────────────────────────────────────

    def showRecordsPanel_(self, _):
        if not self._rw:
            sw = NSScreen.mainScreen().frame().size.width
            sh = NSScreen.mainScreen().frame().size.height
            pw, ph = 600.0, 680.0
            pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
            mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
                    | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
            self._rw = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._rw.setReleasedWhenClosed_(False)
            self._rw.setMinSize_(NSMakeRect(0, 0, 480, 400).size)
            self._rw.setLevel_(NSFloatingWindowLevel)
            self._rw.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            self._rw.setContentView_(self._wkview(NSMakeRect(0, 0, pw, ph)))
        lang = self._app_vm.lang
        self._rw.setTitle_("re.set — 今日记录" if lang == "zh" else "re.set — Today's Records")
        self._load_url(self._rw.contentView(), "/records")
        self._rw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    # ── Preferences window ────────────────────────────────────────────────────

    def showPlanWindow_(self, _):
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pw, ph = 500.0, 420.0
        pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
        mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
                | NSWindowStyleMaskMiniaturizable)
        self._pw = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            pf, mask, NSBackingStoreBuffered, False)
        self._pw.setReleasedWhenClosed_(False)
        self._pw.setLevel_(NSFloatingWindowLevel)
        self._pw.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
        self._pw.setContentView_(self._wkview(NSMakeRect(0, 0, pw, ph)))
        lang = self._app_vm.lang
        self._pw.setTitle_("规划今天" if lang == "zh" else "Plan Today")
        self._load_url(self._pw.contentView(), "/plan-today")
        self._pw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def showPreferences_(self, _):
        if not self._wp:
            sw = NSScreen.mainScreen().frame().size.width
            sh = NSScreen.mainScreen().frame().size.height
            pw, ph = 520.0, 560.0
            pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
            mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
                    | NSWindowStyleMaskMiniaturizable)
            self._wp = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._wp.setReleasedWhenClosed_(False)
            self._wp.setLevel_(NSFloatingWindowLevel)
            self._wp.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            self._wp.setContentView_(self._wkview(NSMakeRect(0, 0, pw, ph)))
        lang = self._app_vm.lang
        self._wp.setTitle_("re.set — 设置" if lang == "zh" else "re.set — Preferences")
        self._load_url(self._wp.contentView(), "/preferences")
        self._wp.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
