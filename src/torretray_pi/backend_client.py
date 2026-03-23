from __future__ import annotations

from datetime import date
from typing import Any

import requests

from torretray_pi.models import Reservation, ReservationFilters


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

    def mark_printed(self, meal_status_id: int) -> None:
        self._request("PATCH", f"/meal-status/{meal_status_id}/printed")

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = requests.request(
                method=method,
                url=f"{self._base_url}{path}",
                params=params,
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
