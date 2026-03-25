from __future__ import annotations

import shutil
import sys
import types
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
if "requests" not in sys.modules:
    sys.modules["requests"] = types.SimpleNamespace(
        RequestException=Exception,
        Response=object,
        request=lambda *args, **kwargs: None,
    )

from torretray_pi.backend_client import BackendClientError  # noqa: E402
from torretray_pi.local_state import LocalReservationStateStore  # noqa: E402
from torretray_pi.models import (  # noqa: E402
    MealType,
    Reservation,
    ReservationFilters,
    ReservationStatus,
    ReservationType,
)
from torretray_pi.services import ReservationService  # noqa: E402


def build_reservation(
    reservation_id: int,
    *,
    status: ReservationStatus = ReservationStatus.NONE,
) -> Reservation:
    return Reservation(
        id=reservation_id,
        user_id=reservation_id,
        name=f"User {reservation_id}",
        meal_type=MealType.LUNCH,
        reservation_type=ReservationType.TRAY,
        diet=None,
        preferences=None,
        date=date(2026, 3, 25),
        status=status,
    )


class FakePrinterService:
    def __init__(self) -> None:
        self.printed_ids: list[int] = []

    def print_ticket(
        self,
        reservation: Reservation,
        _filters: ReservationFilters,
    ) -> None:
        self.printed_ids.append(reservation.id)


class FakeBackendClient:
    def __init__(self) -> None:
        self.reservations: list[Reservation] = []
        self.mark_printed_calls: list[int] = []
        self.cancel_reservation_calls: list[int] = []
        self.update_status_calls: list[tuple[int, ReservationStatus]] = []
        self.fail_mark_printed = False
        self.fail_update_status = False

    def sync_day(self, _target_date: date) -> dict[str, object]:
        return {"ok": True}

    def list_reservations(self, _filters: ReservationFilters) -> list[Reservation]:
        return list(self.reservations)

    def mark_printed(self, meal_status_id: int) -> None:
        self.mark_printed_calls.append(meal_status_id)
        if self.fail_mark_printed:
            raise BackendClientError("backend offline")

    def cancel_reservation(self, meal_status_id: int) -> None:
        self.cancel_reservation_calls.append(meal_status_id)
        if self.fail_update_status:
            raise BackendClientError("backend offline")

    def update_status(
        self,
        meal_status_id: int,
        status: ReservationStatus,
    ) -> None:
        self.update_status_calls.append((meal_status_id, status))
        if self.fail_update_status:
            raise BackendClientError("backend offline")


class LocalPrintSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parent
        self.temp_dir = root / f"_tmp_local_print_sync_{self.id().split('.')[-1]}"
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.client = FakeBackendClient()
        self.printer = FakePrinterService()
        self.local_state = LocalReservationStateStore(self.temp_dir / "state.sqlite3")
        self.filters = ReservationFilters(
            date=date(2026, 3, 25),
            meal_type=MealType.LUNCH,
            reservation_type=ReservationType.TRAY,
        )
        self.service = ReservationService(
            client=self.client,
            printer=self.printer,
            local_state=self.local_state,
            now_provider=lambda: datetime(2026, 3, 25, 12, 0),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_snapshot_applies_local_printed_override(self) -> None:
        self.client.fail_mark_printed = True
        self.local_state.queue_printed(1)
        self.client.reservations = [
            build_reservation(1, status=ReservationStatus.NONE),
            build_reservation(2, status=ReservationStatus.NONE),
        ]

        snapshot = self.service.load_snapshot(self.filters, sync=False)

        self.assertEqual([reservation.id for reservation in snapshot.unprinted], [2])
        self.assertEqual([reservation.id for reservation in snapshot.printed], [1])

    def test_print_reservations_marks_local_when_backend_is_offline(self) -> None:
        self.client.fail_mark_printed = True

        result = self.service.print_reservations(
            [build_reservation(7)],
            self.filters,
            mark_as_printed=True,
        )

        self.assertEqual(result.printed_count, 1)
        self.assertEqual(result.marked_count, 1)
        self.assertEqual(result.synced_count, 0)
        self.assertEqual(result.marked_reservation_ids, [7])
        self.assertTrue(self.local_state.has_pending())

    def test_cancel_reservation_marks_local_when_backend_is_offline(self) -> None:
        self.client.fail_update_status = True

        result = self.service.cancel_reservation(build_reservation(9))

        self.assertEqual(result.updated_count, 1)
        self.assertEqual(result.synced_count, 0)
        self.assertEqual(result.reservation_ids, [9])
        self.assertEqual(result.status, ReservationStatus.CANCELLED)
        self.assertTrue(self.local_state.has_pending())

    def test_load_snapshot_applies_local_cancelled_override(self) -> None:
        self.client.fail_update_status = True
        self.local_state.queue_cancelled(3)
        self.client.reservations = [
            build_reservation(3, status=ReservationStatus.NONE),
            build_reservation(4, status=ReservationStatus.PRINTED),
        ]

        snapshot = self.service.load_snapshot(self.filters, sync=False)

        self.assertEqual([reservation.id for reservation in snapshot.unprinted], [])
        self.assertEqual([reservation.id for reservation in snapshot.printed], [4])

    def test_sync_pending_status_updates_clears_queue_once_backend_returns(self) -> None:
        self.local_state.queue_printed(11)
        self.local_state.queue_cancelled(12)

        synced_count = self.service.sync_pending_status_updates()

        self.assertEqual(synced_count, 2)
        self.assertFalse(self.local_state.has_pending())
        self.assertEqual(self.client.mark_printed_calls, [11])
        self.assertEqual(
            self.client.update_status_calls,
            [(12, ReservationStatus.CANCELLED)],
        )


if __name__ == "__main__":
    unittest.main()
