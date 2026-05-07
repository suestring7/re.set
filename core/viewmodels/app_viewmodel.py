from __future__ import annotations
import time
from datetime import datetime

from ..models.app_config import AppConfig, INTERVAL_PRESETS, DAILY_MINIMUMS
from ..models.checkin import CheckIn
from ..models.daily_record import DailyRecord
from ..services.persistence import PersistenceService
from ..services.scoring import all_minimums_met
from ..timer.break_timer import BreakTimer, TimerState
from ..utils.date_helpers import elapsed_minutes_since, now_hhmm
from ..utils.observable import Observable

_MI: dict[str, dict] = {
    "zh": {
        "timer_fmt":  lambda m, s: f"下次休息：{m:02d}:{s:02d}",
        "snooze_fmt": lambda m, s: f"已推迟：{m:02d}:{s:02d}",
    },
    "en": {
        "timer_fmt":  lambda m, s: f"Next break: {m:02d}:{s:02d}",
        "snooze_fmt": lambda m, s: f"Snoozed: {m:02d}:{s:02d}",
    },
}


class AppViewModel:
    def __init__(
        self,
        persistence: PersistenceService,
        timer: BreakTimer,
        config: AppConfig,
    ) -> None:
        self._persistence = persistence
        self._timer       = timer
        self._config      = config
        self._skip_exercise = False

        # Observable state — subscribed to by the platform layer
        self.timer_display_text: Observable[str]       = Observable("—")
        self.is_away_mode:       Observable[bool]      = Observable(False)
        self.is_end_of_day:      Observable[bool]      = Observable(False)
        self.show_break_window:  Observable[bool]      = Observable(False)
        self.show_warning_panel: Observable[bool]      = Observable(False)
        self.today_record:       Observable[DailyRecord] = Observable(
            persistence.load_state()
        )

        # Wire timer callbacks
        timer.on_warning = self._on_warning
        timer.on_break   = self._on_break
        timer.on_tick    = self._on_tick

    # ── Timer callbacks ───────────────────────────────────────────────────────

    def _fmt(self, key: str, m: int, s: int) -> str:
        return _MI.get(self._config.lang, _MI["zh"])[key](m, s)

    def _on_tick(self, state: TimerState) -> None:
        rem = state.time_remaining
        m, s = rem // 60, rem % 60
        if state.snooze_until > 0:
            sr = max(0, int(state.snooze_until - time.time()))
            text = self._fmt("snooze_fmt", sr // 60, sr % 60)
        else:
            text = self._fmt("timer_fmt", m, s)
        self.timer_display_text.value = text
        self.is_away_mode.value  = state.is_away_mode
        self.is_end_of_day.value = state.is_end_of_day

    def _on_warning(self) -> None:
        self.show_warning_panel.value = True

    def _on_break(self, _kind: str) -> None:
        self.show_warning_panel.value = False
        self.show_break_window.value  = True

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def lang(self) -> str:
        return self._config.lang

    @property
    def skip_exercise(self) -> bool:
        return self._skip_exercise

    def get_status_dict(self) -> dict:
        record = self.today_record.value
        counts = record.category_counts
        state  = self._timer.get_state()
        elapsed_min = 0
        if record.checkins:
            elapsed_min = elapsed_minutes_since(record.checkins[-1].time)
        return {
            **record.to_dict(),
            "daily_minimums":          DAILY_MINIMUMS,
            "all_minimums_met":        all_minimums_met(counts),
            "snooze_available":        self._timer.snooze_available,
            "active_seconds":          state.active_seconds,
            "time_remaining_seconds":  state.time_remaining,
            "suggested_focus_minutes": elapsed_min,
            "skip_exercise":           self._skip_exercise,
            "away_mode":               state.is_away_mode,
            "away_seconds":            self._timer.away_elapsed_seconds,
            "lang":                    self._config.lang,
            "done_for_today":          state.is_end_of_day,
        }

    # ── Commands ─────────────────────────────────────────────────────────────

    def pause_timer(self) -> None:
        self._timer.enter_away_mode()

    def resume_from_away(self) -> int:
        """Exit away mode and return elapsed away seconds."""
        return self._timer.exit_away_mode()

    def trigger_break_now(self) -> None:
        self._timer.trigger_break_now()

    def snooze(self) -> bool:
        return self._timer.snooze()

    def postpone_warning(self) -> dict:
        result = self._timer.postpone_warning()
        if result.get("success"):
            self.show_warning_panel.value = False
        return result

    def release_break_lock(self, reset_active: bool = False) -> None:
        self._timer.release_break_lock(reset_active=reset_active)

    def hide_break_window(self) -> None:
        self.show_break_window.value = False

    def hide_warning_panel(self) -> None:
        self.show_warning_panel.value = False

    def toggle_end_of_day(self) -> bool:
        new_state = not self._timer.done_for_today
        self._timer.set_end_of_day(new_state)
        self.is_end_of_day.value = new_state
        if new_state:
            record = self.today_record.value
            self._persistence.archive_today(record)
            self._persistence._write_daily_summary(record)
        return new_state

    def update_interval(self, minutes: int) -> None:
        if minutes not in INTERVAL_PRESETS:
            return
        self._timer.set_interval_seconds(minutes * 60)
        self._config.interval_minutes = minutes
        self._persistence.update_config(interval_minutes=minutes)

    def update_lang(self, lang: str) -> None:
        if lang not in ("zh", "en"):
            return
        self._config.lang = lang
        self._persistence.update_config(lang=lang)

    def commit_checkin(self, checkin: CheckIn) -> None:
        record = self._persistence.load_state()
        if checkin.exercise:
            eid = checkin.exercise.get("id", "")
            if eid and eid not in record.completed_exercises:
                record.completed_exercises.append(eid)
            cat = checkin.exercise.get("category", "")
            if cat:
                record.category_counts[cat] = record.category_counts.get(cat, 0) + 1
        record.total_score   += checkin.score
        record.focus_minutes += checkin.focus_minutes
        record.checkins.append(checkin)
        self._persistence.save_state(record)
        self._persistence.write_log_entry(record, checkin)
        self.today_record.value = record
        self._skip_exercise = False
        self._timer.reset_cycle()

    def commit_away_checkin(self, checkin: CheckIn) -> None:
        record = self._persistence.load_state()
        record.total_score   += checkin.score
        record.focus_minutes += checkin.focus_minutes
        record.checkins.append(checkin)
        self._persistence.save_state(record)
        self._persistence.write_log_entry(record, checkin)
        self.today_record.value = record
        self._skip_exercise = False
        self._timer.reset_cycle()

    def commit_return_log(
        self,
        before_leave: CheckIn | None,
        away_return: CheckIn,
    ) -> None:
        """Atomically append the pre-leave and away-return checkins."""
        record = self._persistence.load_state()
        if before_leave:
            record.total_score   += before_leave.score
            record.focus_minutes += before_leave.focus_minutes
            record.checkins.append(before_leave)
            self._persistence.write_log_entry(record, before_leave)
        record.total_score   += away_return.score
        record.focus_minutes += away_return.focus_minutes
        record.checkins.append(away_return)
        self._persistence.save_state(record)
        self._persistence.write_log_entry(record, away_return)
        self.today_record.value = record
        self._skip_exercise = (away_return.activity_type == "restroom")
