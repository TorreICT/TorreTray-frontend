from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from torretray_pi.backend_client import BackendClient, BackendClientError
from torretray_pi.local_state import LocalReservationStateStore
from torretray_pi.models import Reservation, ReservationFilters, ReservationStatus
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
    synced_count: int
    marked_reservation_ids: list[int]


@dataclass(frozen=True)
class StatusUpdateResult:
    updated_count: int
    synced_count: int
    reservation_ids: list[int]
    status: ReservationStatus


class ReservationService:
    """Compose backend and printer operations into UI-friendly actions."""

    def __init__(
        self,
        client: BackendClient,
        printer: PrinterService,
        local_state: LocalReservationStateStore,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._client = client
        self._printer = printer
        self._local_state = local_state
        self._now_provider = now_provider or datetime.now

    def load_snapshot(
        self,
        filters: ReservationFilters,
        *,
        sync: bool,
    ) -> ReservationSnapshot:
        self.sync_pending_status_updates()
        sync_result = self._client.sync_day(filters.date) if sync else None
        reservations = self._local_state.apply_status_overrides(
            self._client.list_reservations(filters)
        )
        unprinted = [reservation for reservation in reservations if reservation.is_pending]
        printed = [reservation for reservation in reservations if reservation.is_printed]
        return ReservationSnapshot(
            filters=filters,
            unprinted=sorted(unprinted, key=lambda item: item.name.lower()),
            printed=sorted(printed, key=lambda item: item.name.lower()),
            refreshed_at=self._now_provider(),
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
        synced_count = 0
        marked_reservation_ids: list[int] = []

        for reservation in reservations:
            self._printer.print_ticket(reservation, filters)
            printed_count += 1
            if mark_as_printed and reservation.is_pending:
                self._local_state.queue_printed(reservation.id)
                marked_count += 1
                marked_reservation_ids.append(reservation.id)
                try:
                    self._client.mark_printed(reservation.id)
                except BackendClientError:
                    continue
                self._local_state.mark_synced(reservation.id)
                synced_count += 1

        return PrintJobResult(
            printed_count=printed_count,
            marked_count=marked_count,
            synced_count=synced_count,
            marked_reservation_ids=marked_reservation_ids,
        )

    def cancel_reservation(self, reservation: Reservation) -> StatusUpdateResult:
        self._local_state.queue_cancelled(reservation.id)
        synced_count = 0
        try:
            self._client.cancel_reservation(reservation.id)
        except BackendClientError:
            pass
        else:
            self._local_state.mark_synced(reservation.id)
            synced_count = 1

        return StatusUpdateResult(
            updated_count=1,
            synced_count=synced_count,
            reservation_ids=[reservation.id],
            status=ReservationStatus.CANCELLED,
        )

    def sync_pending_status_updates(self) -> int:
        synced_count = 0
        for reservation_id, status in self._local_state.pending_updates():
            try:
                if status is ReservationStatus.PRINTED:
                    self._client.mark_printed(reservation_id)
                else:
                    self._client.update_status(reservation_id, status)
            except BackendClientError:
                continue
            self._local_state.mark_synced(reservation_id)
            synced_count += 1
        return synced_count

    def has_pending_status_sync(self) -> bool:
        return self._local_state.has_pending()
