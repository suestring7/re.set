from __future__ import annotations
from ..models.activity_type import ActivityType
from ..models.app_config import AppConfig, INTERVAL_PRESETS
from ..services.persistence import PersistenceService


class PreferencesViewModel:
    def __init__(self, persistence: PersistenceService, config: AppConfig) -> None:
        self._persistence = persistence
        self._config      = config

    def get_prefs(self) -> dict:
        return {
            "interval_minutes":     self._config.interval_minutes,
            "warning_advance_seconds": self._config.warning_advance_seconds,
            "reminder_enabled":     self._config.reminder_enabled,
            "lang":                 self._config.lang,
            "interval_presets":     list(INTERVAL_PRESETS),
            "activity_types":       [t.to_dict() for t in self._persistence.load_activity_types()],
            "menu_features":        dict(self._config.menu_features),
            "plan_file_path":       self._config.plan_file_path,
            "plan_file_keyword":    self._config.plan_file_keyword,
            "plan_prefix_type":     self._config.plan_prefix_type,
            "plan_prefix_custom":   self._config.plan_prefix_custom,
            "plan_keyword_not_found": self._config.plan_keyword_not_found,
        }

    def save_plan_settings(self, data: dict) -> None:
        from ..models.app_config import _DEFAULT_MENU_FEATURES
        updates: dict = {}
        for key in ("plan_file_path", "plan_file_keyword", "plan_prefix_type",
                    "plan_prefix_custom", "plan_keyword_not_found"):
            if key in data:
                val = str(data[key])
                setattr(self._config, key, val)
                updates[key] = val
        
        if "warning_advance_seconds" in data:
            try:
                val = int(data["warning_advance_seconds"])
                self._config.warning_advance_seconds = val
                updates["warning_advance_seconds"] = val
            except (TypeError, ValueError):
                pass
        
        if "reminder_enabled" in data:
            val = bool(data["reminder_enabled"])
            self._config.reminder_enabled = val
            updates["reminder_enabled"] = val

        if "menu_features" in data and isinstance(data["menu_features"], dict):
            merged = {**_DEFAULT_MENU_FEATURES, **self._config.menu_features}
            for k, v in data["menu_features"].items():
                if k in _DEFAULT_MENU_FEATURES:
                    merged[k] = bool(v)
            self._config.menu_features = merged
            updates["menu_features"] = merged
        if updates:
            self._persistence.update_config(**updates)

    def load_activity_types(self) -> list[ActivityType]:
        return self._persistence.load_activity_types()

    def save_activity_types(self, raw_types: list[dict]) -> int:
        cleaned: list[ActivityType] = []
        for tp in raw_types:
            if isinstance(tp, dict) and tp.get("id") and tp.get("label") and tp.get("color"):
                cleaned.append(ActivityType.from_dict(tp))
        if cleaned:
            self._persistence.save_activity_types(cleaned)
        return len(cleaned)
