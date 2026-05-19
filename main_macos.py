#!/usr/bin/env python3
"""
re.set macOS entry point — MVVM refactor.

Wire-up order:
  MacOSAdapter → PersistenceService → AppConfig
  ExerciseService
  BreakTimer(adapter)
  AppViewModel(persistence, timer, config)
  RecordsViewModel, PreferencesViewModel
  MacOSController(app_vm, resource_dir) — NSObject / AppDelegate
  HTTP server → dispatch to MacOSController
  timer.start() → app.run()
"""
from __future__ import annotations
import socket
import sys
import threading
from pathlib import Path

from AppKit import NSApplication, NSApplicationActivationPolicyAccessory

from core.models.app_config import PORT
from core.services.exercise_service import ExerciseService
from core.services.persistence import PersistenceService
from core.timer.break_timer import BreakTimer
from core.viewmodels.app_viewmodel import AppViewModel
from core.viewmodels.preferences_viewmodel import PreferencesViewModel
from core.viewmodels.records_viewmodel import RecordsViewModel
from platforms.macos.adapter import MacOSAdapter
from platforms.macos.controller import MacOSController
from platforms.macos.http_server import create_server


def _is_already_running() -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", PORT))
        s.close()
        return result == 0
    except Exception:
        return False


def _resource_dir() -> Path:
    """Resolve UI/resource directory for both dev and bundled-app contexts."""
    if getattr(sys, "frozen", False) or ".app/Contents/MacOS" in str(sys.argv[0] or ""):
        try:
            from AppKit import NSBundle
            rp = NSBundle.mainBundle().resourcePath()
            if rp:
                return Path(str(rp))
        except Exception:
            pass
    # Dev: HTML files live in ui/ next to this file
    here = Path(__file__).parent
    ui = here / "ui"
    return ui if ui.exists() else here


def main() -> None:
    if _is_already_running():
        print("Already running — exiting duplicate instance.")
        sys.exit(0)

    resource_dir = _resource_dir()

    adapter     = MacOSAdapter()
    data_dir    = adapter.data_dir()
    persistence = PersistenceService(
        data_dir=data_dir,
        default_types_file=resource_dir / "activity_types.json",
    )
    config      = persistence.load_config()
    timer       = BreakTimer(
        adapter=adapter,
        interval_seconds=config.interval_seconds(),
        warning_advance_seconds=config.warning_advance_seconds,
        reminders_enabled=config.reminder_enabled,
    )

    app_vm      = AppViewModel(persistence=persistence, timer=timer, config=config)
    records_vm  = RecordsViewModel(persistence=persistence)
    prefs_vm    = PreferencesViewModel(persistence=persistence, config=config)

    exercise_svc = ExerciseService(
        resource_dir / "exercises.json",
        user_file=data_dir / "user_exercises.json",
    )

    # NSApplication must be created before any NSObject subclass
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    controller = MacOSController.alloc().initWithAppViewModel_resourceDir_(
        app_vm, resource_dir
    )
    app.setDelegate_(controller)

    def dispatch(sel: str, arg=None) -> None:
        controller.performSelectorOnMainThread_withObject_waitUntilDone_(
            sel, arg, False)

    server = create_server(
        port=PORT,
        app_vm=app_vm,
        records_vm=records_vm,
        prefs_vm=prefs_vm,
        exercise_svc=exercise_svc,
        resource_dir=resource_dir,
        dispatch_fn=dispatch,
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"HTTP on 0.0.0.0:{PORT}", flush=True)

    timer.start()
    print(
        f"Timer started  interval={config.interval_minutes}min  lang={config.lang}",
        flush=True,
    )

    app.run()


if __name__ == "__main__":
    main()
