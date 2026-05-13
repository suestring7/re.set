# re.set — Project Guide for Claude

## Architecture Overview

re.set is a macOS menu-bar break reminder. The code is split into three layers:

```
core/           Pure Python — zero OS imports. models, services, viewmodels, timer, utils.
platforms/      OS-specific adapters.
  macos/        PyObjC: MacOSAdapter, MacOSController (NSObject/AppDelegate), HTTP server.
ui/             HTML/JS files served over localhost:18030. Cross-platform, never OS-specific.
main_macos.py   Entry point: wires MacOSAdapter → PersistenceService → AppConfig →
                BreakTimer → AppViewModel → RecordsViewModel → PreferencesViewModel →
                MacOSController → HTTP server → app.run()
```

**Cross-platform portability is a first-class constraint.** `core/` must compile and run on Windows with no changes; only `platforms/` is OS-specific.

## PyObjC Selector String Convention (Critical)

PyObjC translates Python method names to ObjC selectors by replacing trailing underscores with colons:

```python
def handlePause_(self, sender): ...   # registers as ObjC selector  handlePause:
def setTitle_forKey_(self, t, k): ... # registers as ObjC selector  setTitle:forKey:
```

**When passing selector strings to NSMenuItem, NSTimer, or `performSelectorOnMainThread`**, use ObjC colon format — never include the trailing underscore before the colon:

```python
# CORRECT
_item("Pause", "handlePause:", target=self)
timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
    1.0, self, "updateStatusBar:", None, True)

# WRONG — creates selector handlePause_: which target never responds to,
# causing macOS to grey out the menu item
_item("Pause", "handlePause_:", target=self)
```

Root symptom of this bug: all menu items appear greyed out except Quit (which targets NSApp, which always responds to `terminate:`).

## Observable Subscriptions Must Be Wired at Startup

`AppViewModel` exposes `Observable[T]` fields (`show_break_window`, `show_warning_panel`, etc.). These are inert until something subscribes. The platform controller must subscribe in `applicationDidFinishLaunching_`, after the controller is fully initialized:

```python
def applicationDidFinishLaunching_(self, _):
    self._setup_status_bar()
    self._setup_subscriptions()   # MUST call — without this, timer-fired breaks never show a window
    ...

@objc.python_method
def _setup_subscriptions(self) -> None:
    def on_break(show: bool) -> None:
        if show:
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showBreakWindow:", url, False)
    self._app_vm.show_break_window.subscribe(on_break)
    ...
```

Without subscriptions, the BreakTimer fires, AppViewModel sets `show_break_window.value = True`, but no UI appears.

## @objc.python_method

Use `@objc.python_method` to hide a method from the ObjC runtime. Required for:
- Private helper methods on NSObject subclasses (e.g. `_setup_subscriptions`, `_L`)
- Any method that takes arguments but has no trailing `_` in its name (would cause arity mismatch with ObjC)

Without this decorator, PyObjC tries to register the method as an ObjC selector and raises `BadPrototypeError` at startup.

## Build & Install

```bash
bash packaging/build_app.sh          # builds dist/re.set.app via py2app
rm -rf ~/Applications/re.set.app
cp -R dist/re.set.app ~/Applications/
```

The build script must be re-run whenever Python source changes — the installed `.app` contains compiled `.pyc` files inside `python314.zip` and will not pick up source edits automatically.

## HTTP API Server

Runs on `localhost:18030`. All UI HTML/JS communicates exclusively through this server. Routes are defined in `platforms/macos/http_server.py`. The HTTP handlers call `AppViewModel` commands directly (never touch AppKit from handler threads — dispatch via `performSelectorOnMainThread` for any UI side effects).

## Dependency Direction

```
platforms/macos/  →  core/  →  (nothing OS-specific)
```

Never import from `platforms/` inside `core/`. Never import AppKit, Quartz, win32api, etc. inside `core/`.

## Key Files

| File | Role |
|------|------|
| `core/timer/break_timer.py` | Timer loop (threading.Timer, 1-second tick). Calls `on_warning`, `on_break`, `on_tick` callbacks. |
| `core/viewmodels/app_viewmodel.py` | Root state: timer display, away mode, break/warning flags. Observable fields. |
| `core/services/persistence.py` | Atomic JSON read/write. Receives `data_dir` from adapter — no hardcoded paths. |
| `platforms/macos/controller.py` | MacOSController: NSStatusItem, NSMenu, WKWebView windows, observable subscriptions. |
| `platforms/macos/http_server.py` | HTTP routes — calls AppViewModel commands, dispatches UI via performSelectorOnMainThread. |
| `ui/plan_today.html` | Plan Today popup (10-min countdown, saves to configured file path via keyword). |
| `setup.py` | py2app build config. Uses patched codesign to handle Python 3.14 / macOS 15+ signature issues. |
