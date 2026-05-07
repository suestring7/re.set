from __future__ import annotations
from dataclasses import dataclass

INTERVAL_PRESETS: list[int] = [15, 20, 25, 30, 45, 60]
DAILY_MINIMUMS: dict[str, int] = {"stretch": 3, "core": 3, "strength": 2}
EYE_TIMER_SECONDS: int = 20
WARNING_ADVANCE: int = 60
SNOOZE_DELAY: int = 5 * 60
IDLE_THRESHOLD: int = 60
MAX_POSTPONES: int = 3
POSTPONE_SECONDS: int = 5 * 60
PORT: int = 18030


@dataclass
class AppConfig:
    interval_minutes: int = 30
    lang: str = "zh"

    def interval_seconds(self) -> int:
        return self.interval_minutes * 60
