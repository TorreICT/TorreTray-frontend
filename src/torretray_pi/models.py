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


class ReservationStatus(str, Enum):
    NONE = "none"
    PRINTED = "printed"
    CANCELLED = "cancelled"


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
        current_date: date | None = None,
    ) -> "ReservationFilters":
        return cls(
            date=current_date or date.today(),
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
    status: ReservationStatus

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
            status=ReservationStatus(str(payload["status"])),
        )

    @property
    def is_pending(self) -> bool:
        return self.status is ReservationStatus.NONE

    @property
    def is_printed(self) -> bool:
        return self.status is ReservationStatus.PRINTED

    @property
    def is_cancelled(self) -> bool:
        return self.status is ReservationStatus.CANCELLED

    @property
    def diet_label(self) -> str:
        return self.diet.strip() if self.diet and self.diet.strip() else "-"

    @property
    def preference_lines(self) -> list[str]:
        if not isinstance(self.preferences, dict):
            return []

        raw_sections = self.preferences.get("sections")
        if not isinstance(raw_sections, list):
            return []

        lines: list[str] = []
        for raw_section in raw_sections:
            if not isinstance(raw_section, dict):
                continue

            section_name = str(raw_section.get("section_name") or "").strip()
            if not section_name:
                continue

            if raw_section.get("selected") is False:
                continue

            if raw_section.get("no_specific_preference"):
                content = "Senza preferenze"
            else:
                selected_dish = raw_section.get("selected_dish")
                if isinstance(selected_dish, str) and selected_dish.strip():
                    content = selected_dish.strip()
                else:
                    continue

            lines.append(f"{section_name}: {content}")

        return lines

    @property
    def preferences_summary(self) -> str:
        lines = self.preference_lines
        if not lines:
            return "Senza preferenze"
        return " | ".join(lines)
