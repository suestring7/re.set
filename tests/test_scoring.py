"""Unit tests for core/services/scoring.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models.activity_type import ActivityType
from core.services.scoring import all_minimums_met, focus_score, session_score


def _act(weight: float) -> ActivityType:
    return ActivityType(id="t", label="T", color="#000", weight=weight)


def test_focus_score_positive_weight():
    assert focus_score(30, _act(1.0)) == 6     # 30 * 1.0 / 5 = 6.0 → 6
    assert focus_score(25, _act(2.0)) == 10    # 25 * 2.0 / 5 = 10.0 → 10
    assert focus_score(0,  _act(3.0)) == 0


def test_focus_score_negative_weight():
    # int() truncates toward zero — matches Python int() semantics
    assert focus_score(10, _act(-1.0)) == -2   # 10 * -1.0 / 5 = -2.0 → -2
    assert focus_score(7,  _act(-5.0)) == -7   # 7 * -5.0 / 5 = -7.0 → -7
    assert focus_score(3,  _act(-5.0)) == -3   # 3 * -5.0 / 5 = -3.0 → -3


def test_focus_score_clamps_weight():
    assert focus_score(10, _act(10.0)) == focus_score(10, _act(5.0))   # clamped at 5
    assert focus_score(10, _act(-10.0)) == focus_score(10, _act(-5.0)) # clamped at -5


def test_focus_score_no_type():
    # Default weight = 1.0
    assert focus_score(20, None) == 4   # 20 * 1.0 / 5 = 4


def test_session_score():
    assert session_score(30, 3, _act(1.0)) == 9   # focus=6, exercise=3
    assert session_score(0,  5, None)       == 5   # focus=0, exercise=5


def test_all_minimums_met():
    assert all_minimums_met({"stretch": 3, "core": 3, "strength": 2}) is True
    assert all_minimums_met({"stretch": 4, "core": 5, "strength": 3}) is True
    assert all_minimums_met({"stretch": 2, "core": 3, "strength": 2}) is False
    assert all_minimums_met({"stretch": 3, "core": 3, "strength": 1}) is False
    assert all_minimums_met({}) is False


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
