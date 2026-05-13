from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from ..models.activity_type import ActivityType
from ..models.app_config import AppConfig, DAILY_MINIMUMS
from ..models.checkin import CheckIn
from ..models.daily_record import DailyRecord
from ..utils.date_helpers import today_str

_DEFAULT_ACTIVITY_TYPES: list[dict] = [
    {"id": "work",          "label": "Work",          "color": "#6366F1", "weight": 1.0},
    {"id": "entertainment", "label": "Entertainment", "color": "#EC4899", "weight": 1.0},
    {"id": "life",          "label": "Life",          "color": "#10B981", "weight": 1.0},
    {"id": "restroom",      "label": "Restroom",      "color": "#B794F4", "weight": 0.0, "parent_id": "life"},
]


class PersistenceService:
    def __init__(self, data_dir: Path, default_types_file: Path | None = None) -> None:
        self._data_dir = data_dir
        self._default_types_file = default_types_file
        data_dir.mkdir(parents=True, exist_ok=True)

    # ── File paths ────────────────────────────────────────────────────────────

    @property
    def _state_file(self) -> Path:
        return self._data_dir / "break_reminder_state.json"

    @property
    def _config_file(self) -> Path:
        return self._data_dir / "config.json"

    @property
    def _activity_types_file(self) -> Path:
        return self._data_dir / "activity_types.json"

    @property
    def _log_file(self) -> Path:
        return self._data_dir / "work_log.txt"

    @property
    def _history_dir(self) -> Path:
        return self._data_dir / "history"

    # ── Daily state ───────────────────────────────────────────────────────────

    def load_state(self) -> DailyRecord:
        if not self._state_file.exists():
            return DailyRecord.empty(today_str())
        try:
            d = json.loads(self._state_file.read_text(encoding="utf-8"))
            if d.get("date") != today_str():
                record = DailyRecord.from_dict(d)
                self._write_daily_summary(record)
                self._archive_state(record)
                return DailyRecord.empty(today_str())
            return DailyRecord.from_dict(d)
        except Exception:
            return DailyRecord.empty(today_str())

    def save_state(self, record: DailyRecord) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        tmp = self._state_file.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(self._state_file)

    # ── Config ────────────────────────────────────────────────────────────────

    def load_config(self) -> AppConfig:
        from ..models.app_config import _DEFAULT_MENU_FEATURES
        try:
            d = json.loads(self._config_file.read_text(encoding="utf-8")) if self._config_file.exists() else {}
            features = {**_DEFAULT_MENU_FEATURES, **d.get("menu_features", {})}
            return AppConfig(
                interval_minutes=int(d.get("interval_minutes", 30)),
                warning_advance_seconds=int(d.get("warning_advance_seconds", 60)),
                reminder_enabled=bool(d.get("reminder_enabled", True)),
                lang=str(d.get("lang", "zh")),
                menu_features=features,
                plan_file_path=str(d.get("plan_file_path", "")),
                plan_file_keyword=str(d.get("plan_file_keyword", "")),
                plan_prefix_type=str(d.get("plan_prefix_type", "none")),
                plan_prefix_custom=str(d.get("plan_prefix_custom", "")),
                plan_keyword_not_found=str(d.get("plan_keyword_not_found", "append")),
            )
        except Exception:
            return AppConfig()

    def update_config(self, **kwargs) -> None:
        try:
            d: dict = {}
            if self._config_file.exists():
                try:
                    d = json.loads(self._config_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            d.update(kwargs)
            self._config_file.write_text(json.dumps(d, indent=2))
        except Exception:
            pass

    # ── Activity types ────────────────────────────────────────────────────────

    def load_activity_types(self) -> list[ActivityType]:
        raw: list[dict] = []
        if self._activity_types_file.exists():
            try:
                raw = json.loads(self._activity_types_file.read_text(encoding="utf-8"))
            except Exception:
                raw = []
        elif self._default_types_file and self._default_types_file.exists():
            try:
                raw = json.loads(self._default_types_file.read_text(encoding="utf-8"))
            except Exception:
                raw = []
        if not raw:
            raw = list(_DEFAULT_ACTIVITY_TYPES)
        result = [ActivityType.from_dict(d) for d in raw if isinstance(d, dict) and d.get("id")]
        return result or [ActivityType.from_dict(d) for d in _DEFAULT_ACTIVITY_TYPES]

    def save_activity_types(self, types: list[ActivityType]) -> None:
        self._activity_types_file.write_text(
            json.dumps([t.to_dict() for t in types], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── History ───────────────────────────────────────────────────────────────

    def _archive_state(self, record: DailyRecord) -> None:
        if not record.date:
            return
        self._history_dir.mkdir(exist_ok=True)
        p = self._history_dir / f"{record.date}.json"
        if not p.exists():
            try:
                p.write_text(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
            except Exception:
                pass

    def archive_today(self, record: DailyRecord) -> None:
        self._archive_state(record)

    def load_history_list(self) -> dict[str, dict]:
        self._history_dir.mkdir(exist_ok=True)
        result: dict[str, dict] = {}
        for f in self._history_dir.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                result[f.stem] = {
                    "total_score":   d.get("total_score", 0),
                    "focus_minutes": d.get("focus_minutes", 0),
                    "checkins":      len(d.get("checkins", [])),
                }
            except Exception:
                pass
        return result

    def load_history_date(self, date_str: str) -> DailyRecord | None:
        if date_str == today_str():
            return self.load_state()
        p = self._history_dir / f"{date_str}.json"
        if p.exists():
            try:
                return DailyRecord.from_dict(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        return None

    def save_history_date(self, record: DailyRecord) -> None:
        if record.date == today_str():
            self.save_state(record)
            return
        self._history_dir.mkdir(exist_ok=True)
        p = self._history_dir / f"{record.date}.json"
        p.write_text(
            json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── Logging ───────────────────────────────────────────────────────────────

    def append_work_log(self, text: str) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(text)

    def write_log_entry(self, record: DailyRecord, checkin: CheckIn) -> None:
        ns = datetime.now().strftime("%Y-%m-%d %H:%M")
        ex = checkin.exercise
        act = (f"动作：{ex['name']} {ex['id']} (+{ex['score']}分)" if ex else "动作：跳过")
        fm = checkin.focus_minutes
        self.append_work_log(
            f"[{ns}] 专注 {fm}min (+{fm//5}分) | {act} | "
            f"本次 +{checkin.score}分 | 今日累计 {record.total_score}分 | "
            f"内容：{checkin.work_content}\n"
        )

    def _write_daily_summary(self, record: DailyRecord) -> None:
        if not record.checkins:
            return
        counts = record.category_counts
        fm = record.focus_minutes
        h, m = fm // 60, fm % 60
        fs_str = f"{h}小时{m}分钟" if h else f"{m}分钟"
        s_ok = counts.get("stretch", 0) >= DAILY_MINIMUMS["stretch"]
        c_ok = counts.get("core", 0) >= DAILY_MINIMUMS["core"]
        t_ok = counts.get("strength", 0) >= DAILY_MINIMUMS["strength"]
        exc = sum(1 for c in record.checkins if c.exercise)
        names = [c.exercise["name"] for c in record.checkins if c.exercise]
        fs = sum(c.focus_minutes // 5 for c in record.checkins)
        self.append_work_log(
            f"\n===== {record.date} 日报 =====\n"
            f"总专注时长：{fs_str}\n"
            f"完成动作：{exc}个（"
            f"拉伸{counts.get('stretch',0)}{'✅' if s_ok else '❌'}/"
            f"核心{counts.get('core',0)}{'✅' if c_ok else '❌'}/"
            f"力量+水瓶{counts.get('strength',0)}{'✅' if t_ok else '❌'}）\n"
            f"保底达标：{'✅ 全部完成' if (s_ok and c_ok and t_ok) else '❌ 未全部完成'}\n"
            f"动作积分：{record.total_score - fs}分 | 专注积分：{fs}分 | 总分：{record.total_score}分\n"
            f"完成动作列表：{', '.join(names) if names else '无'}\n"
            f"============================\n\n"
        )
