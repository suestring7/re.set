from __future__ import annotations
import json
import random
from pathlib import Path

from ..models.app_config import DAILY_MINIMUMS
from ..models.daily_record import DailyRecord
from ..models.exercise import Exercise


class ExerciseService:
    def __init__(self, exercises_file: Path) -> None:
        self._file = exercises_file
        self._cache: list[Exercise] | None = None

    def load(self) -> list[Exercise]:
        if self._cache is None:
            with open(self._file, encoding="utf-8") as f:
                self._cache = [Exercise.from_dict(d) for d in json.load(f)]
        return self._cache

    def pick_exercises(self, record: DailyRecord) -> list[Exercise]:
        """3-phase selection: fill deficits first, then unused categories, then any."""
        all_exs = self.load()
        completed = set(record.completed_exercises)
        counts = record.category_counts

        available = [e for e in all_exs if e.id not in completed] or list(all_exs)
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
