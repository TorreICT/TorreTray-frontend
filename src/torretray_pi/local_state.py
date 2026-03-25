from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from torretray_pi.models import Reservation, ReservationStatus


class LocalReservationStateStore:
    """Persist local reservation status overrides until backend sync succeeds."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def queue_printed(self, meal_status_id: int) -> None:
        self.queue_status(meal_status_id, ReservationStatus.PRINTED)

    def queue_cancelled(self, meal_status_id: int) -> None:
        self.queue_status(meal_status_id, ReservationStatus.CANCELLED)

    def queue_status(self, meal_status_id: int, status: ReservationStatus) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO pending_status_updates (meal_status_id, status, queued_at)
                VALUES (?, ?, ?)
                ON CONFLICT(meal_status_id) DO UPDATE SET
                    status = excluded.status,
                    queued_at = excluded.queued_at
                """,
                (
                    meal_status_id,
                    status.value,
                    datetime.now(UTC).isoformat(timespec="seconds"),
                ),
            )

    def mark_synced(self, meal_status_id: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM pending_status_updates WHERE meal_status_id = ?",
                (meal_status_id,),
            )

    def pending_updates(self) -> list[tuple[int, ReservationStatus]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT meal_status_id, status
                FROM pending_status_updates
                ORDER BY queued_at ASC, meal_status_id ASC
                """
            ).fetchall()
        return [(int(row[0]), ReservationStatus(str(row[1]))) for row in rows]

    def has_pending(self) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM pending_status_updates LIMIT 1"
            ).fetchone()
        return row is not None

    def apply_status_overrides(
        self,
        reservations: list[Reservation],
    ) -> list[Reservation]:
        pending_updates = dict(self.pending_updates())
        if not pending_updates:
            return reservations

        merged: list[Reservation] = []
        for reservation in reservations:
            override_status = pending_updates.get(reservation.id)
            if override_status is None or reservation.status is override_status:
                merged.append(reservation)
                continue
            merged.append(replace(reservation, status=override_status))
        return merged

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_status_updates (
                    meal_status_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL,
                    queued_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection
