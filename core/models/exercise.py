from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Exercise:
    id: str
    name: str
    name_en: str
    description: str
    description_en: str
    category: str  # 'stretch' | 'core' | 'strength'
    muscle_groups: list[str]
    score: int
    requires_standing: bool = False
    requires_props: bool = False
    duration_seconds: int = 0
    sets: int = 0
    duration_per_set: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> Exercise:
        return cls(
            id=d["id"],
            name=d["name"],
            name_en=d.get("name_en", ""),
            description=d.get("description", ""),
            description_en=d.get("description_en", ""),
            category=d["category"],
            muscle_groups=list(d.get("muscle_groups", [])),
            score=int(d.get("score", 1)),
            requires_standing=bool(d.get("requires_standing", False)),
            requires_props=bool(d.get("requires_props", False)),
            duration_seconds=int(d.get("duration_seconds", 0)),
            sets=int(d.get("sets", 0)),
            duration_per_set=int(d.get("duration_per_set", 0)),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "description": self.description,
            "description_en": self.description_en,
            "category": self.category,
            "muscle_groups": self.muscle_groups,
            "score": self.score,
            "requires_standing": self.requires_standing,
            "requires_props": self.requires_props,
            "duration_seconds": self.duration_seconds,
            "sets": self.sets,
            "duration_per_set": self.duration_per_set,
        }
