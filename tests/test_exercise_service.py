"""Unit tests for core/services/exercise_service.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models.daily_record import DailyRecord
from core.services.exercise_service import ExerciseService

_EXERCISES_FILE = Path(__file__).parent.parent / "exercises.json"


def _svc() -> ExerciseService:
    return ExerciseService(_EXERCISES_FILE)


def test_load_returns_37_exercises():
    exs = _svc().load()
    assert len(exs) == 37


def test_pick_returns_3():
    record = DailyRecord.empty("2026-01-01")
    result = _svc().pick_exercises(record)
    assert len(result) == 3


def test_pick_covers_all_three_categories_when_fresh():
    record = DailyRecord.empty("2026-01-01")
    # Run many times to catch randomness failures
    svc = _svc()
    for _ in range(20):
        cats = {e.category for e in svc.pick_exercises(record)}
        assert cats == {"stretch", "core", "strength"}, f"Missing category: {cats}"


def test_pick_fills_deficits_first():
    # Only stretch is below minimum — expect at least one stretch in result
    record = DailyRecord(
        date="2026-01-01",
        category_counts={"stretch": 0, "core": 3, "strength": 2},
    )
    svc = _svc()
    for _ in range(10):
        cats = [e.category for e in svc.pick_exercises(record)]
        assert "stretch" in cats, f"Deficit category missing: {cats}"


def test_pick_avoids_completed_exercises_when_possible():
    svc = _svc()
    all_exs = svc.load()
    # Complete all but 3 exercises
    keep = all_exs[-3:]
    keep_ids = {e.id for e in keep}
    record = DailyRecord(
        date="2026-01-01",
        completed_exercises=[e.id for e in all_exs if e.id not in keep_ids],
    )
    for _ in range(10):
        result = svc.pick_exercises(record)
        result_ids = {e.id for e in result}
        assert result_ids <= keep_ids, f"Expected subset of uncompleted: {result_ids}"


def test_pick_falls_back_to_all_when_all_completed():
    svc = _svc()
    all_ids = [e.id for e in svc.load()]
    record = DailyRecord(
        date="2026-01-01",
        completed_exercises=all_ids,
    )
    result = svc.pick_exercises(record)
    assert len(result) == 3


if __name__ == "__main__":
    import traceback
    tests = [fn for name, fn in sorted(globals().items()) if name.startswith("test_")]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(failed)
