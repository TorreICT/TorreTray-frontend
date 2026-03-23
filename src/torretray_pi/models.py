from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any


class MealType(str, Enum):
    LUNCH = "lunch"
    DINNER = "dinner"

    @property
    def label(self) -> str:
        return "Pranzo" if self is MealType.LUNCH else "Cena"


class ReservationType(str, Enum):
    TRAY = "tray"
    LUNCHBOX = "lunchbox"

    @property
    def label(self) -> str:
        return "Vassoi" if self is ReservationType.TRAY else "Schiscette"

    @property
    def ticket_title(self) -> str:
        return (
            "Vassoi Torrescalla"
            if self is ReservationType.TRAY
            else "Schiscette Torrescalla"
        )


@dataclass(frozen=True)
class ReservationFilters:
    date: date
    meal_type: MealType
    reservation_type: ReservationType

    @classmethod
    def today(
        cls,
        *,
        meal_type: MealType,
        reservation_type: ReservationType,
    ) -> "ReservationFilters":
        return cls(
            date=date.today(),
            meal_type=meal_type,
            reservation_type=reservation_type,
        )


@dataclass(frozen=True)
class Reservation:
    id: int
    user_id: int
    name: str
    meal_type: MealType
    reservation_type: ReservationType | None
    diet: str | None
    preferences: dict[str, Any] | None
    date: date
    printed: bool

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Reservation":
        reservation_type = payload.get("reservation_type")
        return cls(
            id=int(payload["id"]),
            user_id=int(payload["user_id"]),
            name=str(payload["name"]).strip(),
            meal_type=MealType(payload["meal_type"]),
            reservation_type=ReservationType(reservation_type) if reservation_type else None,
            diet=payload.get("diet"),
            preferences=payload.get("preferences"),
            date=date.fromisoformat(payload["date"]),
            printed=bool(payload["printed"]),
        )

    @property
    def diet_label(self) -> str:
        return self.diet.strip() if self.diet and self.diet.strip() else "-"

    @property
    def preferences_summary(self) -> str:
        if not self.preferences:
            return "-"

        parts: list[str] = []
        for key, value in self.preferences.items():
            label = key.replace("_", " ").strip().title()
            if isinstance(value, dict):
                selected = value.get("selected_dish")
                if value.get("no_specific_preference"):
                    content = "Nessuna preferenza"
                elif selected:
                    content = str(selected)
                elif value.get("selected") is False:
                    content = "Escluso"
                else:
                    content = "Selezionato"
            else:
                content = str(value)
            parts.append(f"{label}: {content}")
        return " | ".join(parts) if parts else "-"
