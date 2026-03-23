from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from torretray_pi.backend_client import BackendClient
from torretray_pi.models import Reservation, ReservationFilters
from torretray_pi.printing import PrinterService


@dataclass(frozen=True)
class ReservationSnapshot:
    filters: ReservationFilters
    unprinted: list[Reservation]
    printed: list[Reservation]
    refreshed_at: datetime
    sync_result: dict[str, object] | None


@dataclass(frozen=True)
class PrintJobResult:
    printed_count: int
    marked_count: int


class ReservationService:
    """Compose backend and printer operations into UI-friendly actions."""

    def __init__(self, client: BackendClient, printer: PrinterService) -> None:
        self._client = client
        self._printer = printer

    def load_snapshot(
        self,
        filters: ReservationFilters,
        *,
        sync: bool,
    ) -> ReservationSnapshot:
        sync_result = self._client.sync_day(filters.date) if sync else None
        reservations = self._client.list_reservations(filters)
        unprinted = [reservation for reservation in reservations if not reservation.printed]
        printed = [reservation for reservation in reservations if reservation.printed]
        return ReservationSnapshot(
            filters=filters,
            unprinted=sorted(unprinted, key=lambda item: item.name.lower()),
            printed=sorted(printed, key=lambda item: item.name.lower()),
            refreshed_at=datetime.now(),
            sync_result=sync_result,
        )

    def print_reservations(
        self,
        reservations: list[Reservation],
        filters: ReservationFilters,
        *,
        mark_as_printed: bool,
    ) -> PrintJobResult:
        printed_count = 0
        marked_count = 0

        for reservation in reservations:
            self._printer.print_ticket(reservation, filters)
            printed_count += 1
            if mark_as_printed and not reservation.printed:
                self._client.mark_printed(reservation.id)
                marked_count += 1

        return PrintJobResult(
            printed_count=printed_count,
            marked_count=marked_count,
        )
