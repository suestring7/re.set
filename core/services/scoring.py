from __future__ import annotations
from ..models.activity_type import ActivityType
from ..models.app_config import DAILY_MINIMUMS


def focus_score(minutes: int, activity_type: ActivityType | None) -> int:
    """int(minutes * weight / 5) — truncates toward zero for negative weights."""
    minutes = max(0, int(minutes))
    weight = activity_type.weight if activity_type else 1.0
    weight = max(-5.0, min(5.0, weight))
    return int(minutes * weight / 5)


def session_score(
    focus_minutes: int,
    exercise_score: int,
    activity_type: ActivityType | None,
) -> int:
    return focus_score(focus_minutes, activity_type) + exercise_score


def all_minimums_met(category_counts: dict[str, int]) -> bool:
    return all(category_counts.get(c, 0) >= m for c, m in DAILY_MINIMUMS.items())
