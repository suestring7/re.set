from __future__ import annotations
from datetime import date, datetime


def today_str() -> str:
    return date.today().isoformat()


def now_hhmm() -> str:
    return datetime.now().strftime("%H:%M")


def elapsed_minutes_since(hhmm: str) -> int:
    """Minutes since the given HH:MM time string (same day; handles midnight edge)."""
    try:
        lh, lm = map(int, hhmm.split(":"))
        now_dt = datetime.now()
        last_dt = now_dt.replace(hour=lh, minute=lm, second=0, microsecond=0)
        diff = (now_dt - last_dt).total_seconds()
        if diff < 0:
            diff += 86400
        return max(0, int(diff / 60))
    except Exception:
        return 0
