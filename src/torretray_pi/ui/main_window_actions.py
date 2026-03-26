from __future__ import annotations

from dataclasses import replace

from PyQt5 import QtWidgets

from torretray_pi.config import load_settings, save_runtime_settings
from torretray_pi.models import Reservation, ReservationStatus
from torretray_pi.services import (
    PrintJobResult,
    ReservationService,
    ReservationSnapshot,
    StatusUpdateResult,
)
from torretray_pi.ui.dialogs import ConfirmationDialog, TraySettingsDialog


class MainWindowActionMixin:
    """Operator-triggered actions such as settings, print, and cancel."""

    def _open_settings_dialog(self) -> None:
        dialog = TraySettingsDialog(settings=self.settings, parent=self)
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            self.statusBar().showMessage("Nessuna impostazione modificata.", 3000)
            return

        values = dialog.values()
        save_runtime_settings(
            self.settings.project_root,
            auto_refresh_minutes=values["auto_refresh_minutes"],
            loading_time_before_meal=values["loading_time_before_meal"],
            bell_time_before_meal=values["bell_time_before_meal"],
            schedule_lookahead_days=values["schedule_lookahead_days"],
            bell_interval_seconds=values["bell_interval_seconds"],
            bell_muted=values["bell_muted"],
        )

        self.settings = load_settings(test_now_override=self.settings.test_now)
        self.service = ReservationService(
            client=self.client,
            printer=self.printer,
            local_state=self.local_state,
            now_provider=self.settings.current_datetime,
        )
        self._bell_player.set_muted(self.settings.bell_muted)
        self.statusBar().showMessage("Impostazioni salvate correttamente.", 5000)
        self._evaluate_schedule(force_refresh=True, show_loading=False)

    def _print_pending_batch(self) -> None:
        reservations = self._snapshot.unprinted if self._snapshot else []
        self._start_print_job(
            reservations=reservations,
            mark_as_printed=True,
            title="Conferma stampa",
            message=(
                "Sei sicuro di voler stampare tutti i ticket da stampare?\n\n"
                "Suggerimento: usa prima 'Aggiorna' per sincronizzare gli ultimi dati."
            ),
        )

    def _print_single_pending(self, reservation: Reservation) -> None:
        self._start_print_job(
            reservations=[reservation],
            mark_as_printed=True,
            title="Conferma stampa",
            message=(
                f"Stampare il ticket per {reservation.name}?\n\n"
                "Suggerimento: usa prima 'Aggiorna' per sincronizzare gli ultimi dati."
            ),
        )

    def _reprint_single(self, reservation: Reservation) -> None:
        self._start_print_job(
            reservations=[reservation],
            mark_as_printed=False,
            title="Conferma ristampa",
            message=(
                f"Ristampare il ticket per {reservation.name}?\n\n"
                "Suggerimento: se vuoi verificare gli ultimi dati, usa prima 'Aggiorna'."
            ),
        )

    def _cancel_single_pending(self, reservation: Reservation) -> None:
        if not reservation.is_pending:
            self.statusBar().showMessage(
                "Solo le prenotazioni non ancora stampate possono essere annullate.",
                4000,
            )
            return

        dialog = ConfirmationDialog(
            title="Conferma annullamento",
            message=(
                f"Annullare la prenotazione per {reservation.name}?\n\n"
                "La prenotazione verra rimossa dalla lista operativa del tray."
            ),
            parent=self,
        )
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            self.statusBar().showMessage("Operazione annullata.", 3000)
            return

        self._run_task(
            task=lambda: self.service.cancel_reservation(reservation),
            on_success=lambda result: self._on_cancel_success(reservation, result),
            on_finished=lambda: self._evaluate_schedule(
                force_refresh=True,
                show_loading=False,
            ),
            loading_message="Annullando prenotazione...",
        )

    def _reprint_all_printed(self) -> None:
        reservations = self._snapshot.printed if self._snapshot else []
        self._start_print_job(
            reservations=reservations,
            mark_as_printed=False,
            title="Conferma ristampa",
            message=(
                "Sei sicuro di voler ristampare tutti i ticket gia stampati?\n\n"
                "Suggerimento: se vuoi verificare gli ultimi dati, usa prima 'Aggiorna'."
            ),
        )

    def _start_print_job(
        self,
        *,
        reservations: list[Reservation],
        mark_as_printed: bool,
        title: str,
        message: str,
    ) -> None:
        if not reservations:
            self.statusBar().showMessage(
                "Nessun ticket disponibile per questa azione.",
                4000,
            )
            return
        if self._active_filters is None:
            self.statusBar().showMessage("Nessuna fascia attiva per la stampa.", 4000)
            return

        dialog = ConfirmationDialog(title=title, message=message, parent=self)
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            self.statusBar().showMessage("Operazione annullata.", 3000)
            return

        self._run_task(
            task=lambda: self.service.print_reservations(
                reservations,
                self._active_filters,
                mark_as_printed=mark_as_printed,
            ),
            on_success=self._on_print_success,
            on_finished=lambda: self._evaluate_schedule(
                force_refresh=True,
                show_loading=False,
            ),
            loading_message="Stampando...",
        )

    def _on_print_success(self, result: object) -> None:
        if not isinstance(result, PrintJobResult):
            return
        self._apply_local_status_result(
            StatusUpdateResult(
                updated_count=result.marked_count,
                synced_count=result.synced_count,
                reservation_ids=result.marked_reservation_ids,
                status=ReservationStatus.PRINTED,
            )
        )
        deferred_count = result.marked_count - result.synced_count
        if result.marked_count:
            if deferred_count:
                self.statusBar().showMessage(
                    (
                        f"Stampati {result.printed_count} ticket e aggiornati "
                        f"{result.marked_count} stati in locale. "
                        f"{deferred_count} in attesa di sync backend."
                    ),
                    6000,
                )
            else:
                self.statusBar().showMessage(
                    (
                        f"Stampati {result.printed_count} ticket e "
                        f"aggiornati {result.marked_count} stati."
                    ),
                    5000,
                )
        else:
            self.statusBar().showMessage(
                f"Stampati {result.printed_count} ticket.",
                5000,
            )

    def _on_cancel_success(
        self,
        reservation: Reservation,
        result: object,
    ) -> None:
        if not isinstance(result, StatusUpdateResult):
            return
        self._apply_local_status_result(result)
        deferred_count = result.updated_count - result.synced_count
        if deferred_count:
            self.statusBar().showMessage(
                (
                    f"Prenotazione annullata per {reservation.name} in locale. "
                    f"{deferred_count} update in attesa di sync backend."
                ),
                6000,
            )
            return

        self.statusBar().showMessage(
            f"Prenotazione annullata per {reservation.name}.",
            5000,
        )

    def _apply_local_status_result(self, result: StatusUpdateResult) -> None:
        if self._snapshot is None or not result.updated_count:
            return

        marked_ids = set(result.reservation_ids)
        still_pending: list[Reservation] = []
        newly_printed: list[Reservation] = []
        for reservation in self._snapshot.unprinted:
            if reservation.id in marked_ids:
                if result.status is ReservationStatus.PRINTED:
                    newly_printed.append(
                        replace(reservation, status=ReservationStatus.PRINTED)
                    )
            else:
                still_pending.append(reservation)

        if result.status is ReservationStatus.CANCELLED:
            self._snapshot = ReservationSnapshot(
                filters=self._snapshot.filters,
                unprinted=sorted(still_pending, key=lambda item: item.name.lower()),
                printed=self._snapshot.printed,
                refreshed_at=self._snapshot.refreshed_at,
                sync_result=self._snapshot.sync_result,
            )
            self._render_snapshot_tables()
            self._refresh_action_states()
            return

        if not newly_printed:
            return

        printed = sorted(
            [*self._snapshot.printed, *newly_printed],
            key=lambda item: item.name.lower(),
        )
        self._snapshot = ReservationSnapshot(
            filters=self._snapshot.filters,
            unprinted=sorted(still_pending, key=lambda item: item.name.lower()),
            printed=printed,
            refreshed_at=self._snapshot.refreshed_at,
            sync_result=self._snapshot.sync_result,
        )
        self._render_snapshot_tables()
        self._refresh_action_states()
