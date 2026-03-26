from __future__ import annotations

from datetime import date, datetime, timedelta

from PyQt5 import QtCore

from torretray_pi.config import ScheduledServiceWindow, next_service, resolve_active_service
from torretray_pi.models import Reservation
from torretray_pi.services import ReservationSnapshot


class MainWindowScheduleMixin:
    """Schedule evaluation, refresh orchestration, and bell timing."""

    def _evaluate_schedule(
        self,
        *,
        force_refresh: bool,
        show_loading: bool,
        allow_schedule_refresh: bool = True,
    ) -> None:
        now = self.settings.current_datetime()
        self._sync_pending_status_updates_in_background()
        if allow_schedule_refresh and self._schedule_refresh_needed(now, force_refresh):
            self._refresh_schedule(
                force_data_refresh=force_refresh,
                show_loading=show_loading,
            )
            return

        active_service, service_changed = self._set_active_service_for(now)
        if service_changed:
            self._reset_snapshot_view()
        self._sync_bell_scheduler(now, force=service_changed or force_refresh)

        if active_service is None:
            if force_refresh:
                self._refresh_idle_day(show_loading=show_loading)
            else:
                self._apply_idle_state(now)
            return

        self._update_active_context(now, active_service)
        if force_refresh or service_changed or self._refresh_due(now):
            self.refresh_data(sync=True, show_loading=show_loading)
        else:
            self._refresh_action_states()

    def _manual_refresh(self) -> None:
        if self._busy:
            return

        start_date, end_date = self._schedule_query_range()
        self.statusBar().showMessage(
            f"Aggiornamento orari dal backend: {start_date.isoformat()} -> {end_date.isoformat()}",
            5000,
        )
        self._run_task(
            task=lambda: self.client.list_meal_schedules(
                start_date=start_date,
                end_date=end_date,
            ),
            on_success=self._apply_manual_schedule_refresh,
            loading_message="Aggiornando orari e prenotazioni...",
        )

    def _refresh_schedule(self, *, force_data_refresh: bool, show_loading: bool) -> None:
        if self._busy:
            return

        start_date, end_date = self._schedule_query_range()
        self._run_task(
            task=lambda: self.client.list_meal_schedules(
                start_date=start_date,
                end_date=end_date,
            ),
            on_success=lambda windows: self._apply_schedule_windows(
                windows,
                force_data_refresh=force_data_refresh,
            ),
            loading_message="Caricando orari..." if show_loading else None,
        )

    def _apply_schedule_windows(
        self,
        schedule_windows: list[ScheduledServiceWindow],
        *,
        force_data_refresh: bool,
    ) -> None:
        self._set_backend_connection_down(False)
        self._store_schedule_windows(schedule_windows)
        self._continue_after_schedule_refresh(force_data_refresh=force_data_refresh)

    def _apply_manual_schedule_refresh(
        self,
        schedule_windows: list[ScheduledServiceWindow],
    ) -> None:
        self._set_backend_connection_down(False)
        self._store_schedule_windows(schedule_windows)
        self._continue_manual_refresh()

    def _continue_after_schedule_refresh(self, *, force_data_refresh: bool) -> None:
        """Resume refresh flow after schedule loading fully releases the busy state."""
        QtCore.QTimer.singleShot(
            0,
            lambda: self._evaluate_schedule(
                force_refresh=force_data_refresh,
                show_loading=False,
                allow_schedule_refresh=False,
            ),
        )

    def _continue_manual_refresh(self) -> None:
        """Recompute state from the latest schedule memory, then sync reservations."""
        QtCore.QTimer.singleShot(0, self._finish_manual_refresh)

    def _finish_manual_refresh(self) -> None:
        now = self.settings.current_datetime()
        active_service, service_changed = self._set_active_service_for(now)
        if service_changed:
            self._reset_snapshot_view()
        self._sync_bell_scheduler(now, force=True)

        if active_service is None:
            self.statusBar().showMessage(
                "Orari aggiornati in memoria. Nessuna fascia attiva: eseguo solo la sync giornaliera.",
                5000,
            )
            self._last_auto_refresh_at = None
            self._refresh_idle_day(show_loading=False)
            return

        self._update_active_context(now, active_service)
        self.statusBar().showMessage(
            f"Orari aggiornati in memoria. Fascia attiva rilevata: {active_service.label}.",
            5000,
        )
        self.refresh_data(sync=True, show_loading=False)

    def _schedule_query_range(self) -> tuple[date, date]:
        start_date = self.settings.current_date()
        lookahead_days = max(1, self.settings.schedule_lookahead_days)
        end_date = start_date + timedelta(days=lookahead_days - 1)
        return start_date, end_date

    def refresh_data(self, sync: bool, show_loading: bool) -> None:
        if self._busy:
            return
        if self._active_filters is None:
            self._apply_idle_state(self.settings.current_datetime())
            return

        self._run_task(
            task=lambda: self.service.load_snapshot(self._active_filters, sync=sync),
            on_success=self._apply_snapshot,
            loading_message="Aggiornando..." if show_loading else None,
        )

    def _apply_snapshot(self, snapshot: ReservationSnapshot) -> None:
        self._set_backend_connection_down(False)
        self._snapshot = snapshot
        self._last_auto_refresh_at = snapshot.refreshed_at
        self._render_snapshot_tables()

        if self._active_service is not None:
            self._update_active_context(snapshot.refreshed_at, self._active_service)

        self._set_last_update_label(snapshot.refreshed_at)
        if snapshot.sync_result is not None:
            self.statusBar().showMessage("Dati sincronizzati correttamente", 5000)
        else:
            self.statusBar().showMessage("Lista aggiornata", 3000)
        self._refresh_action_states()

    def _refresh_idle_day(self, *, show_loading: bool) -> None:
        if self._busy:
            return

        target_date = self.settings.current_date()
        self._run_task(
            task=lambda: self.client.sync_day(target_date),
            on_success=self._apply_idle_refresh_result,
            loading_message="Aggiornando..." if show_loading else None,
        )

    def _apply_idle_refresh_result(self, _sync_result: object) -> None:
        self._set_backend_connection_down(False)
        refreshed_at = self.settings.current_datetime()
        self._apply_idle_state(refreshed_at, refreshed_at=refreshed_at)
        self.statusBar().showMessage(
            "Orari ricaricati e sync giornaliera completata",
            5000,
        )

    def _apply_idle_state(
        self,
        now: datetime,
        *,
        refreshed_at: datetime | None = None,
    ) -> None:
        self._snapshot = None
        self._render_reservation_tables([], [])
        self._set_last_update_label(refreshed_at)

        upcoming_service = next_service(
            self._schedule_windows,
            current_moment=now,
            loading_time_before_meal=self.settings.loading_time_before_meal,
        )
        if upcoming_service is None:
            self.context_label.setText("Fuori fascia oraria automatica.")
            self.mode_description.setText(
                "Nessuna fascia configurata disponibile nei prossimi giorni."
            )
        else:
            service, loading_time = upcoming_service
            bell_time = self._bell_window_starts_at(service)
            self.context_label.setText(
                f"Fuori fascia oraria. Prossimo caricamento: {service.label} alle "
                f"{loading_time.strftime('%H:%M')}. Campanella dalle "
                f"{bell_time.strftime('%H:%M')}."
            )
            self.mode_description.setText(
                f"Carica {self.settings.loading_time_before_meal} min prima. "
                f"Refresh ogni {self.settings.auto_refresh_minutes} min."
            )
        self.statusBar().showMessage("Fuori fascia oraria automatica", 3000)
        self._refresh_action_states()

    def _update_active_context(
        self,
        current_moment: datetime,
        active_service: ScheduledServiceWindow,
    ) -> None:
        bell_start = self._bell_window_starts_at(active_service)
        phase_label = (
            "Precaricamento attivo"
            if current_moment < active_service.starts_at()
            else "Fascia attiva"
        )

        self.context_label.setText(
            f"{phase_label}: {active_service.label} fino alle "
            f"{active_service.end_time.strftime('%H:%M')}."
        )
        self.mode_description.setText(
            f"Refresh ogni {self.settings.auto_refresh_minutes} min. "
            f"Campanella da {bell_start.strftime('%H:%M')}."
        )

    def _refresh_action_states(self) -> None:
        pending = bool(self._snapshot and self._snapshot.unprinted)
        printed = bool(self._snapshot and self._snapshot.printed)
        self.print_pending_button.setEnabled(pending and not self._busy)
        self.reprint_all_button.setEnabled(printed and not self._busy)
        self.refresh_button.setEnabled(not self._busy)
        self.settings_button.setEnabled(not self._busy)

    def _handle_bell_timer(self) -> None:
        self._ring_if_needed()
        self._sync_bell_scheduler(
            self.settings.current_datetime() + timedelta(microseconds=1),
            force=True,
        )

    def _ring_if_needed(self) -> None:
        now = self.settings.current_datetime()
        if self._busy or self._snapshot is None or not self._bell_is_allowed(now):
            return
        if self._snapshot.unprinted:
            self._bell_player.ring()

    def _sync_bell_scheduler(
        self,
        now: datetime | None = None,
        *,
        force: bool = False,
    ) -> None:
        reference_time = now or self.settings.current_datetime()
        if (
            not force
            and self.bell_timer.isActive()
            and self._next_bell_check_at is not None
            and reference_time <= self._next_bell_check_at
        ):
            return

        self.bell_timer.stop()
        self._next_bell_check_at = self._next_bell_check_time(reference_time)
        if self._next_bell_check_at is None:
            return

        delay_ms = max(
            0,
            int((self._next_bell_check_at - reference_time).total_seconds() * 1000),
        )
        self.bell_timer.start(delay_ms)

    def _next_bell_check_time(self, now: datetime) -> datetime | None:
        if self._active_service is None:
            return None

        bell_start = self._bell_window_starts_at(self._active_service)
        service_end = self._active_service.ends_at()
        if now > service_end:
            return None
        if now <= bell_start:
            return bell_start

        interval_seconds = self.settings.bell_interval_seconds
        elapsed_seconds = (now - bell_start).total_seconds()
        completed_intervals = int(elapsed_seconds // interval_seconds)
        next_check = bell_start + timedelta(
            seconds=(completed_intervals + 1) * interval_seconds
        )
        if next_check > service_end:
            return None
        return next_check

    def _bell_is_allowed(self, now: datetime) -> bool:
        if self._active_service is None:
            return False
        return (
            self._bell_window_starts_at(self._active_service)
            <= now
            <= self._active_service.ends_at()
        )

    def _bell_window_starts_at(self, service: ScheduledServiceWindow) -> datetime:
        return max(
            service.loading_starts_at(self.settings.loading_time_before_meal),
            service.bell_starts_at(self.settings.bell_time_before_meal),
        )

    def _store_schedule_windows(
        self,
        schedule_windows: list[ScheduledServiceWindow],
    ) -> None:
        self._schedule_windows = sorted(
            schedule_windows,
            key=lambda window: (window.date, window.start_time, window.key),
        )
        self._schedule_loaded_at = self.settings.current_datetime()

    def _set_active_service_for(
        self,
        now: datetime,
    ) -> tuple[ScheduledServiceWindow | None, bool]:
        active_service = resolve_active_service(
            self._schedule_windows,
            current_moment=now,
            loading_time_before_meal=self.settings.loading_time_before_meal,
        )
        service_changed = self._service_key(active_service) != self._service_key(
            self._active_service
        )
        self._active_service = active_service
        self._active_filters = (
            active_service.filters_for() if active_service is not None else None
        )
        return active_service, service_changed

    def _reset_snapshot_view(self) -> None:
        self._snapshot = None
        self._last_auto_refresh_at = None
        self._render_reservation_tables([], [])
        self._set_last_update_label(None)

    def _render_snapshot_tables(self) -> None:
        if self._snapshot is None:
            self._render_reservation_tables([], [])
            return
        self._render_reservation_tables(
            self._snapshot.unprinted,
            self._snapshot.printed,
        )

    def _render_reservation_tables(
        self,
        unprinted: list[Reservation],
        printed: list[Reservation],
    ) -> None:
        self.pending_table.set_reservations(unprinted)
        self.printed_table.set_reservations(printed)

    def _set_last_update_label(self, refreshed_at: datetime | None) -> None:
        if refreshed_at is None:
            self.status_label.setText("Ultimo aggiornamento: N/D")
            return
        self.status_label.setText(
            f"Ultimo aggiornamento: {refreshed_at.strftime('%d/%m/%Y %H:%M:%S')}"
        )

    def _refresh_due(self, now: datetime) -> bool:
        if self._last_auto_refresh_at is None:
            return True
        elapsed_seconds = (now - self._last_auto_refresh_at).total_seconds()
        return elapsed_seconds >= self.settings.auto_refresh_minutes * 60

    @staticmethod
    def _service_key(service: ScheduledServiceWindow | None) -> str | None:
        if service is None:
            return None
        return f"{service.date.isoformat()}:{service.key}"

    def _schedule_refresh_needed(self, now: datetime, force_refresh: bool) -> bool:
        if force_refresh or not self._schedule_windows or self._schedule_loaded_at is None:
            return True
        if (now - self._schedule_loaded_at).total_seconds() >= (
            self.settings.auto_refresh_minutes * 60
        ):
            return True
        _start_date, covered_until = self._schedule_query_range()
        return not any(window.date >= covered_until for window in self._schedule_windows)
