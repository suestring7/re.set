from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class CheckIn:
    time: str                       # "HH:MM"
    focus_minutes: int
    score: int
    exercise: dict[str, Any] | None = None
    work_content: str = ""
    activity_type: str | None = None
    event_type: str = "break"       # break | away_return | before_leave | away_session | restroom
    start_time: str | None = None
    end_time: str | None = None
    mood: str | None = None         # great | good | okay | tired | stressed
    note: str = ""                  # free-form feelings, optional

    @classmethod
    def from_dict(cls, d: dict) -> CheckIn:
        return cls(
            time=d.get("time", ""),
            focus_minutes=int(d.get("focus_minutes", 0) or 0),
            score=int(d.get("score", 0) or 0),
            exercise=d.get("exercise") or None,
            work_content=str(d.get("work_content", "") or ""),
            activity_type=d.get("activity_type") or None,
            event_type=str(d.get("event_type", "break")),
            start_time=d.get("start_time") or None,
            end_time=d.get("end_time") or None,
            mood=d.get("mood") or None,
            note=str(d.get("note", "") or ""),
        )

    def to_dict(self) -> dict:
        d: dict = {
            "time": self.time,
            "focus_minutes": self.focus_minutes,
            "score": self.score,
            "exercise": self.exercise,
            "work_content": self.work_content,
            "activity_type": self.activity_type,
            "event_type": self.event_type,
        }
        if self.start_time is not None:
            d["start_time"] = self.start_time
        if self.end_time is not None:
            d["end_time"] = self.end_time
        if self.mood is not None:
            d["mood"] = self.mood
        if self.note:
            d["note"] = self.note
        return d
