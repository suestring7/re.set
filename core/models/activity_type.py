from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ActivityType:
    id: str
    label: str
    color: str
    weight: float = 1.0
    parent_id: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> ActivityType:
        try:
            w = float(d.get("weight", 1.0))
        except (TypeError, ValueError):
            w = 1.0
        return cls(
            id=d["id"],
            label=d.get("label", d["id"]),
            color=d.get("color", "#999999"),
            weight=max(-5.0, min(5.0, w)),
            parent_id=d.get("parent_id") or None,
        )

    def to_dict(self) -> dict:
        d: dict = {
            "id": self.id,
            "label": self.label,
            "color": self.color,
            "weight": self.weight,
        }
        if self.parent_id:
            d["parent_id"] = self.parent_id
        return d
