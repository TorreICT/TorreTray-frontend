from __future__ import annotations

from datetime import date, datetime
from typing import Any

import requests

from torretray_pi.config import ScheduledServiceWindow
from torretray_pi.models import (
    MealType,
    Reservation,
    ReservationFilters,
    ReservationStatus,
    ReservationType,
)


class BackendClientError(RuntimeError):
    """Raised when the TorreTray backend cannot satisfy a request."""


class BackendClient:
    """Small synchronous client for the TorreTray backend API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def sync_day(self, target_date: date) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "/meal-status/sync",
            params={"date": target_date.isoformat()},
        )
        if not isinstance(payload, dict):
            raise BackendClientError(
                "La sync del backend ha restituito una risposta inattesa."
            )
        return payload

    def list_reservations(self, filters: ReservationFilters) -> list[Reservation]:
        payload = self._request(
            "GET",
            "/meal-status/reservations",
            params={
                "date": filters.date.isoformat(),
                "meal_type": filters.meal_type.value,
                "reservation_type": filters.reservation_type.value,
            },
        )
        if not isinstance(payload, list):
            raise BackendClientError(
                "Il backend ha restituito prenotazioni in un formato inatteso."
            )
        return [
            Reservation.from_payload(item)
            for item in payload
            if isinstance(item, dict)
        ]

    def list_meal_schedules(
        self,
        *,
        start_date: date,
        end_date: date,
    ) -> list[ScheduledServiceWindow]:
        payload = self._request(
            "GET",
            "/meal-schedules",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        if not isinstance(payload, list):
            raise BackendClientError(
                "Il backend ha restituito gli orari pasti in un formato inatteso."
            )

        windows: list[ScheduledServiceWindow] = []
        for raw_day in payload:
            if not isinstance(raw_day, dict):
                continue
            raw_date = raw_day.get("date")
            raw_windows = raw_day.get("windows", [])
            if not isinstance(raw_date, str):
                continue
            try:
                target_date = date.fromisoformat(raw_date)
            except ValueError:
                continue

            for raw_window in raw_windows:
                if not isinstance(raw_window, dict):
                    continue
                try:
                    windows.append(
                        ScheduledServiceWindow(
                            date=target_date,
                            key=str(raw_window["service_key"]),
                            label=str(raw_window["label"]),
                            meal_type=MealType(str(raw_window["meal_type"])),
                            reservation_type=ReservationType(
                                str(raw_window["reservation_type"])
                            ),
                            start_time=datetime.strptime(
                                str(raw_window["start_time"]),
                                "%H:%M",
                            ).time(),
                            end_time=datetime.strptime(
                                str(raw_window["end_time"]),
                                "%H:%M",
                            ).time(),
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    continue
        return windows

    def mark_printed(self, meal_status_id: int) -> None:
        self._request("PATCH", f"/meal-status/{meal_status_id}/printed")

    def update_status(self, meal_status_id: int, status: ReservationStatus) -> None:
        self._request(
            "PATCH",
            f"/meal-status/{meal_status_id}/status",
            json_body={"status": status.value},
        )

    def cancel_reservation(self, meal_status_id: int) -> None:
        self.update_status(meal_status_id, ReservationStatus.CANCELLED)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = requests.request(
                method=method,
                url=f"{self._base_url}{path}",
                params=params,
                json=json_body,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            raise BackendClientError(
                "Impossibile contattare il backend TorreTray."
            ) from exc

        if response.status_code >= 400:
            raise BackendClientError(self._extract_error_message(response))

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise BackendClientError(
                "Il backend ha restituito una risposta non valida."
            ) from exc

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f"Errore backend {response.status_code}."

        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail.strip():
                return detail
        return f"Errore backend {response.status_code}."
