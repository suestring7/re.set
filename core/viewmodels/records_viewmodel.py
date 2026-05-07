from __future__ import annotations
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
