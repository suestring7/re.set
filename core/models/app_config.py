from __future__ import annotations
from dataclasses import dataclass, field

INTERVAL_PRESETS: list[int] = [15, 20, 25, 30, 45, 60]
DAILY_MINIMUMS: dict[str, int] = {"stretch": 3, "core": 3, "strength": 2}
EYE_TIMER_SECONDS: int = 20
WARNING_ADVANCE: int = 60
SNOOZE_DELAY: int = 5 * 60
IDLE_THRESHOLD: int = 60
MAX_POSTPONES: int = 3
POSTPONE_SECONDS: int = 5 * 60
PORT: int = 18030

_DEFAULT_MENU_FEATURES: dict[str, bool] = {
    "plan_today":    True,
    "away_tracking": True,
    "trigger_break": True,
    "view_records":  True,
    "end_of_day":    True,
}


@dataclass
class AppConfig:
    interval_minutes: int = 30
    warning_advance_seconds: int = 60
    reminder_enabled: bool = True
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

    def interval_seconds(self) -> int:
        return self.interval_minutes * 60

    def feature_enabled(self, key: str) -> bool:
        return bool(self.menu_features.get(key, True))
