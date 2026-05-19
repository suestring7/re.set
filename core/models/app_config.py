from __future__ import annotations
from dataclasses import dataclass, field

INTERVAL_PRESETS: list[int] = [15, 20, 25, 30, 45, 60]
DAILY_MINIMUMS: dict[str, int] = {"stretch": 3, "core": 3, "strength": 2}
EYE_TIMER_SECONDS: int = 20
WARNING_ADVANCE: int = 90
SNOOZE_DELAY: int = 5 * 60
IDLE_THRESHOLD: int = 60
MAX_POSTPONES: int = 3
POSTPONE_SECONDS: int = 5 * 60
PORT: int = 18030

_DEFAULT_MENU_FEATURES: dict[str, bool] = {
    "plan_today":          True,
    "away_tracking":       True,
    "trigger_break":       True,
    "view_records":        True,
    "end_of_day":          True,
    "restroom_analytics":  True,
}


@dataclass
class AppConfig:
    interval_minutes: int = 30
    lang: str = "zh"
    # Which menu items are visible
    menu_features: dict = field(
        default_factory=lambda: dict(_DEFAULT_MENU_FEATURES))
    # Plan Today settings
    plan_file_path:         str = ""
    plan_file_keyword:      str = ""
    plan_prefix_type:       str = "none"   # none | date | time | datetime | custom
    plan_prefix_custom:     str = ""       # template with {date}/{time} tokens
    plan_keyword_not_found: str = "append" # append | error
    # Daily-file mode: if set, plan_file_path is a directory and this pattern
    # is used to build today's filename (YYYY-MM-DD.md → %Y-%m-%d.md)
    plan_file_pattern:      str = ""
    # User-tunable reminder behaviour (see also WARNING_ADVANCE constant)
    warning_advance_seconds: int = WARNING_ADVANCE
    reminder_enabled: bool = True
    # Sound feedback — NSSound preset names; empty string = silent
    reminder_sound: str = "Ping"
    done_sound:     str = "Tink"
    # Exercise preferences — used by ExerciseService to filter pool
    exercise_standing: bool = True   # allow standing exercises
    exercise_props:    bool = True   # allow exercises requiring props
    exercise_max_difficulty: int = 3 # 1|2|3
    pain_flags: list[str] = field(default_factory=list)  # e.g. ["lower_back", "wrist"]
    # Scheduled full-screen alerts: [{id, time, message, enabled}]
    scheduled_alerts: list[dict] = field(default_factory=list)

    def interval_seconds(self) -> int:
        return self.interval_minutes * 60

    def feature_enabled(self, key: str) -> bool:
        return bool(self.menu_features.get(key, True))
