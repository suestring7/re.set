from __future__ import annotations
from dataclasses import dataclass, field
from .checkin import CheckIn


@dataclass
class DailyRecord:
    date: str
    checkins: list[CheckIn] = field(default_factory=list)
    total_score: int = 0
    focus_minutes: int = 0
    category_counts: dict[str, int] = field(
        default_factory=lambda: {"stretch": 0, "core": 0, "strength": 0}
    )
    completed_exercises: list[str] = field(default_factory=list)

    @classmethod
    def empty(cls, date: str) -> DailyRecord:
        return cls(date=date)

    @classmethod
    def from_dict(cls, d: dict) -> DailyRecord:
        return cls(
            date=d.get("date", ""),
            checkins=[CheckIn.from_dict(c) for c in d.get("checkins", [])],
            total_score=int(d.get("total_score", 0) or 0),
            focus_minutes=int(d.get("focus_minutes", 0) or 0),
            category_counts=dict(
                d.get("category_counts", {"stretch": 0, "core": 0, "strength": 0})
            ),
            completed_exercises=list(d.get("completed_exercises", [])),
        )

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "checkins": [c.to_dict() for c in self.checkins],
            "total_score": self.total_score,
            "focus_minutes": self.focus_minutes,
            "category_counts": self.category_counts,
            "completed_exercises": self.completed_exercises,
        }
