from __future__ import annotations
import json
import random
from datetime import datetime as _datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ..models.app_config import DAILY_MINIMUMS
from ..models.daily_record import DailyRecord
from ..models.exercise import Exercise

if TYPE_CHECKING:
    from ..models.app_config import AppConfig

_COOLDOWN_MINUTES = 30


def _recent_ids(record: DailyRecord, minutes: int = _COOLDOWN_MINUTES) -> set[str]:
    """Return IDs of exercises completed within the last `minutes` minutes."""
    now = _datetime.now()
    now_mins = now.hour * 60 + now.minute
    recent: set[str] = set()
    for c in record.checkins:
        if not c.exercise or not c.time:
            continue
        try:
            h, m = map(int, c.time.split(':'))
            elapsed = now_mins - (h * 60 + m)
            if 0 <= elapsed <= minutes:
                recent.add(c.exercise.get('id', ''))
        except (ValueError, AttributeError):
            pass
    return recent


class ExerciseService:
    def __init__(self, exercises_file: Path, user_file: Path | None = None) -> None:
        self._file = exercises_file
        self._user_file = user_file  # optional file for user-contributed exercises
        self._cache: list[Exercise] | None = None

    def load(self) -> list[Exercise]:
        if self._cache is None:
            with open(self._file, encoding="utf-8") as f:
                exercises = [Exercise.from_dict(d) for d in json.load(f)]
            if self._user_file and self._user_file.exists():
                with open(self._user_file, encoding="utf-8") as f:
                    exercises += [Exercise.from_dict(d) for d in json.load(f)]
            self._cache = exercises
        return self._cache

    def invalidate_cache(self) -> None:
        self._cache = None

    def _apply_user_prefs(self, exercises: list[Exercise], config: "AppConfig") -> list[Exercise]:
        """Filter exercise pool based on user preferences."""
        out = []
        pain_flags = set(getattr(config, "pain_flags", []))
        allow_standing = getattr(config, "exercise_standing", True)
        allow_props = getattr(config, "exercise_props", True)
        max_diff = getattr(config, "exercise_max_difficulty", 3)
        for ex in exercises:
            if not allow_standing and ex.requires_standing:
                continue
            if not allow_props and ex.requires_props:
                continue
            if ex.difficulty > max_diff:
                continue
            if pain_flags and set(ex.pain_contraindications) & pain_flags:
                continue
            out.append(ex)
        return out if out else exercises  # fall back to unfiltered if prefs eliminate everything

    def pick_exercises(self, record: DailyRecord, config: "AppConfig | None" = None) -> list[Exercise]:
        """3-phase selection: fill deficits first, then unused categories, then any.
        Exercises completed in the last 30 minutes are deprioritised.
        User preferences (standing, props, difficulty, pain_flags) filter the pool."""
        raw_exs = self.load()
        all_exs = self._apply_user_prefs(raw_exs, config) if config else raw_exs
        completed = set(record.completed_exercises)
        recent    = _recent_ids(record)
        counts = record.category_counts

        # Prefer exercises not done recently; fall back to all not-completed if needed
        preferred = [e for e in all_exs if e.id not in completed and e.id not in recent]
        fallback  = [e for e in all_exs if e.id not in completed] or list(all_exs)
        available = preferred if preferred else fallback
        by_cat: dict[str, list[Exercise]] = {}
        for ex in available:
            by_cat.setdefault(ex.category, []).append(ex)

        deficits = [
            c for c, m in DAILY_MINIMUMS.items()
            if counts.get(c, 0) < m and by_cat.get(c)
        ]

        result: list[Exercise] = []
        used_ids: set[str] = set()
        used_cats: set[str] = set()

        # Phase 1: categories below their daily minimum
        random.shuffle(deficits)
        for cat in deficits:
            pool = [e for e in by_cat.get(cat, []) if e.id not in used_ids]
            if pool:
                ex = random.choice(pool)
                result.append(ex)
                used_ids.add(ex.id)
                used_cats.add(cat)
            if len(result) == 3:
                break

        # Phase 2: categories not yet represented
        if len(result) < 3:
            for cat in [c for c in by_cat if c not in used_cats]:
                pool = [e for e in by_cat[cat] if e.id not in used_ids]
                if pool:
                    ex = random.choice(pool)
                    result.append(ex)
                    used_ids.add(ex.id)
                    used_cats.add(cat)
                if len(result) == 3:
                    break

        # Phase 3: any remaining exercises
        if len(result) < 3:
            pool = [e for e in available if e.id not in used_ids]
            random.shuffle(pool)
            for ex in pool:
                result.append(ex)
                if len(result) == 3:
                    break

        return result[:3]
