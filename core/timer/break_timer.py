from __future__ import annotations
import threading
import time
from dataclasses import dataclass
from datetime import date as _date
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class PlatformAdapter(Protocol):
    def idle_seconds(self) -> float: ...
    def schedule_midnight_reset(self, callback: Callable[[], None]) -> None: ...
    def on_screen_wake(self, callback: Callable[[], None]) -> None: ...


@dataclass
class TimerState:
    active_seconds: int
    interval_seconds: int
    is_away_mode: bool
    is_end_of_day: bool
    snooze_until: float  # 0.0 when not snoozed

    @property
    def time_remaining(self) -> int:
        return max(0, self.interval_seconds - self.active_seconds)


class BreakTimer:
    """
    Thread-safe active-time accumulator.

    All state mutations happen under _lock.  Callbacks are invoked outside
    the lock (on a fresh daemon thread for on_break) to avoid re-entrant
    deadlocks.
    """

    WARNING_ADVANCE  = 60      # default; instance uses _warning_advance
    IDLE_THRESHOLD   = 60      # Quartz idle seconds → user counts as inactive
    SNOOZE_DELAY     = 5 * 60
    POSTPONE_SECONDS = 5 * 60
    MAX_POSTPONES    = 3

    # Callbacks — set by AppViewModel before calling start()
    on_warning: Callable[[], None] | None = None
    on_break:   Callable[[str], None] | None = None  # "normal" | "snoozed"
    on_tick:    Callable[[TimerState], None] | None = None

    def __init__(
        self,
        adapter: PlatformAdapter,
        interval_seconds: int = 1800,
        *,
        warning_advance_seconds: int = WARNING_ADVANCE,
        reminders_enabled: bool = True,
    ) -> None:
        self._adapter  = adapter
        self._lock     = threading.Lock()
        self._interval = interval_seconds
        self._warning_advance = int(warning_advance_seconds)
        self._reminders_enabled = bool(reminders_enabled)
        self._active   = 0
        self._warning_shown    = False
        self._snooze_available = True
        self._snooze_until     = 0.0
        self._break_locked     = False
        self._away_mode        = False
        self._away_start_ts    = 0.0
        self._done_for_today   = False
        self._done_for_date    = ""
        self._postpone_count   = 0
        self._running          = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self) -> None:
        _last = time.monotonic()
        while self._running:
            time.sleep(1)
            _now = time.monotonic()
            _dt = max(1, round(_now - _last))
            _last = _now
            snoozed_trigger = normal_trigger = show_warn = False

            with self._lock:
                if self._break_locked or self._away_mode:
                    pass  # skip accumulation; on_tick still fires below
                elif self._done_for_today:
                    if self._done_for_date != _date.today().isoformat():
                        self._done_for_today = False
                        self._done_for_date  = ""
                        self._active         = 0
                        self._warning_shown  = False
                    # else: still done for today — skip accumulation, on_tick fires
                elif self._snooze_until > 0:
                    if time.time() >= self._snooze_until:
                        self._snooze_until  = 0.0
                        self._break_locked  = True
                        snoozed_trigger = True
                    # skip accumulation during snooze; on_tick fires
                elif self._reminders_enabled:
                    if self._adapter.idle_seconds() < self.IDLE_THRESHOLD:
                        self._active += _dt
                        remaining = self._interval - self._active

                        if not self._warning_shown and remaining <= self._warning_advance:
                            self._warning_shown = True
                            show_warn = True

                        if remaining <= 0:
                            self._active           = 0
                            self._warning_shown    = False
                            self._snooze_available = True
                            self._break_locked     = True
                            normal_trigger = True
                # reminders disabled: skip accumulation, on_tick still fires

            if show_warn and self.on_warning:
                self.on_warning()

            if snoozed_trigger and self.on_break:
                cb = self.on_break
                threading.Thread(target=lambda: cb("snoozed"), daemon=True).start()

            if normal_trigger and self.on_break:
                cb = self.on_break
                threading.Thread(target=lambda: cb("normal"), daemon=True).start()

            if self.on_tick:
                self.on_tick(self.get_state())

    # ── Commands ─────────────────────────────────────────────────────────────

    def snooze(self) -> bool:
        with self._lock:
            if not self._snooze_available:
                return False
            self._snooze_available = False
            self._snooze_until     = time.time() + self.SNOOZE_DELAY
            return True

    def postpone_warning(self) -> dict:
        with self._lock:
            count = self._postpone_count
            if count >= self.MAX_POSTPONES:
                return {"success": False, "reason": "max_postpones"}
            self._postpone_count = count + 1
            self._active         = max(0, self._active - self.POSTPONE_SECONDS)
            self._warning_shown  = False
        return {"success": True, "postpones_used": count + 1, "max": self.MAX_POSTPONES}

    def enter_away_mode(self) -> None:
        with self._lock:
            self._away_mode      = True
            self._away_start_ts  = time.time()
            self._active         = 0
            self._warning_shown  = False
            self._snooze_until   = 0.0
            self._break_locked   = False

    def exit_away_mode(self) -> int:
        """Clear away mode and return elapsed away seconds."""
        with self._lock:
            away_secs = int(time.time() - self._away_start_ts) if self._away_mode else 0
            self._away_mode        = False
            self._away_start_ts    = 0.0
            self._active           = 0
            self._warning_shown    = False
            self._snooze_available = True
            return away_secs

    def trigger_break_now(self) -> None:
        with self._lock:
            if self._break_locked:
                return
            self._break_locked = True
        if self.on_break:
            cb = self.on_break
            threading.Thread(target=lambda: cb("normal"), daemon=True).start()

    def set_interval_seconds(self, seconds: int) -> None:
        with self._lock:
            self._interval = seconds
            wa = self._warning_advance
            self._active   = min(self._active, seconds - wa - 5)
            if seconds - self._active > wa:
                self._warning_shown = False

    def set_warning_advance_seconds(self, seconds: int) -> None:
        with self._lock:
            self._warning_advance = max(1, int(seconds))
            wa = self._warning_advance
            self._active = min(self._active, self._interval - wa - 5)
            if self._interval - self._active > wa:
                self._warning_shown = False

    def set_reminders_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._reminders_enabled = bool(enabled)
            if not self._reminders_enabled:
                self._warning_shown = False

    def reset_cycle(self) -> None:
        with self._lock:
            self._active           = 0
            self._warning_shown    = False
            self._snooze_available = True
            self._break_locked     = False
            self._postpone_count   = 0

    def release_break_lock(self, reset_active: bool = False) -> None:
        with self._lock:
            self._break_locked = False
            if reset_active:
                self._active = 0

    def set_end_of_day(self, active: bool) -> None:
        with self._lock:
            self._done_for_today = active
            self._done_for_date  = _date.today().isoformat() if active else ""
            if active:
                self._active        = 0
                self._warning_shown = False
                self._snooze_until  = 0.0
                self._break_locked  = False

    # ── Read-only properties ──────────────────────────────────────────────────

    @property
    def away_mode(self) -> bool:
        return self._away_mode

    @property
    def away_elapsed_seconds(self) -> int:
        if not self._away_mode:
            return 0
        return int(time.time() - self._away_start_ts)

    @property
    def done_for_today(self) -> bool:
        return self._done_for_today

    @property
    def snooze_available(self) -> bool:
        return self._snooze_available

    def get_state(self) -> TimerState:
        with self._lock:
            return TimerState(
                active_seconds=self._active,
                interval_seconds=self._interval,
                is_away_mode=self._away_mode,
                is_end_of_day=self._done_for_today,
                snooze_until=self._snooze_until,
            )
