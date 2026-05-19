from __future__ import annotations
from ..models.checkin import CheckIn
from ..models.daily_record import DailyRecord
from ..services.persistence import PersistenceService
from ..utils.date_helpers import today_str


class RecordsViewModel:
    def __init__(self, persistence: PersistenceService) -> None:
        self._persistence = persistence

    def load_today(self) -> DailyRecord:
        return self._persistence.load_state()

    def load_date(self, date_str: str) -> DailyRecord | None:
        return self._persistence.load_history_date(date_str)

    def load_history_list(self) -> dict[str, dict]:
        return self._persistence.load_history_list()

    def edit_checkin(self, date_str: str, index: int, updates: dict) -> bool:
        if date_str == today_str():
            record = self._persistence.load_state()
            is_today = True
        else:
            record = self._persistence.load_history_date(date_str)
            if record is None:
                return False
            is_today = False

        if index < 0 or index >= len(record.checkins):
            return False

        c = record.checkins[index]
        if "time" in updates:
            c.time = str(updates["time"])[:5]
        if "start_time" in updates:
            v = updates["start_time"]
            c.start_time = str(v)[:5] if v else None
        if "end_time" in updates:
            v = updates["end_time"]
            c.end_time = str(v)[:5] if v else None
        if "work_content" in updates:
            c.work_content = str(updates["work_content"])
        if "activity_type" in updates:
            c.activity_type = updates["activity_type"] or None
        if "mood" in updates:
            c.mood = updates["mood"] or None
        if "note" in updates:
            c.note = str(updates["note"] or "")
        if "focus_minutes" in updates:
            try:
                new_fm = max(0, int(updates["focus_minutes"]))
                old_fm = c.focus_minutes
                record.focus_minutes = max(0, record.focus_minutes - old_fm + new_fm)
                c.focus_minutes = new_fm
            except (TypeError, ValueError):
                pass

        if is_today:
            self._persistence.save_state(record)
        else:
            self._persistence.save_history_date(record)
        return True

    def add_checkin(self, date_str: str, data: dict) -> int:
        """Append a new blank checkin and return its index, or -1 on failure."""
        if date_str == today_str():
            record = self._persistence.load_state()
            is_today = True
        else:
            record = self._persistence.load_history_date(date_str)
            if record is None:
                return -1
            is_today = False

        fm = max(0, int(data.get("focus_minutes", 0) or 0))
        t  = str(data.get("time", "") or "")[:5] or None
        st = str(data.get("start_time", "") or "")[:5] or None
        et = str(data.get("end_time", "") or "")[:5] or None
        checkin = CheckIn(
            time=t, start_time=st, end_time=et,
            focus_minutes=fm,
            work_content=str(data.get("work_content", "") or ""),
            activity_type=data.get("activity_type") or None,
            event_type=str(data.get("event_type", "checkin") or "checkin"),
            score=0,
            mood=data.get("mood") or None,
            note=str(data.get("note", "") or ""),
        )
        record.checkins.append(checkin)
        record.focus_minutes += fm
        idx = len(record.checkins) - 1
        if is_today:
            self._persistence.save_state(record)
        else:
            self._persistence.save_history_date(record)
        return idx

    def delete_checkin(self, date_str: str, index: int) -> bool:
        if date_str == today_str():
            record = self._persistence.load_state()
            is_today = True
        else:
            record = self._persistence.load_history_date(date_str)
            if record is None:
                return False
            is_today = False

        if index < 0 or index >= len(record.checkins):
            return False

        removed = record.checkins.pop(index)
        record.total_score   = max(0, record.total_score   - (removed.score          or 0))
        record.focus_minutes = max(0, record.focus_minutes - (removed.focus_minutes  or 0))

        if is_today:
            self._persistence.save_state(record)
        else:
            self._persistence.save_history_date(record)
        return True
