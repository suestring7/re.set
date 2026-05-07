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
            "interval_minutes": self._config.interval_minutes,
            "lang":             self._config.lang,
            "interval_presets": list(INTERVAL_PRESETS),
            "activity_types":   [t.to_dict() for t in self._persistence.load_activity_types()],
        }

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
