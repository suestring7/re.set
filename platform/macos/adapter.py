from __future__ import annotations
from pathlib import Path
from typing import Callable

from core.timer.break_timer import PlatformAdapter


class MacOSAdapter:
    """Isolates all macOS-specific system calls from the portable core."""

    def idle_seconds(self) -> float:
        try:
            import Quartz
            return float(
                Quartz.CGEventSourceSecondsSinceLastEventType(
                    Quartz.kCGEventSourceStateHIDSystemState, 0xFFFFFFFF
                )
            )
        except Exception:
            return 0.0

    def data_dir(self) -> Path:
        return Path.home() / "Library" / "Application Support" / "re.set"

    def schedule_midnight_reset(self, callback: Callable[[], None]) -> None:
        # Midnight reset is handled by the timer loop's date-comparison check.
        # A dedicated NSCalendar notification can be wired here in Phase 5.
        pass

    def on_screen_wake(self, callback: Callable[[], None]) -> None:
        # Wired in MacOSController.applicationDidFinishLaunching_ via NSWorkspace.
        self._screen_wake_callback = callback
