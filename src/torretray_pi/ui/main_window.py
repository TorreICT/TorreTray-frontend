from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, timedelta

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.audio import BellPlayer
from torretray_pi.backend_client import BackendClient
from torretray_pi.config import (
    AppSettings,
    ScheduledServiceWindow,
    load_settings,
    next_service,
    resolve_active_service,
    save_runtime_settings,
)
from torretray_pi.local_state import LocalReservationStateStore
from torretray_pi.models import Reservation, ReservationFilters, ReservationStatus
from torretray_pi.printing import PrinterService
from torretray_pi.services import (
    PrintJobResult,
    ReservationService,
    ReservationSnapshot,
    StatusUpdateResult,
)
from torretray_pi.ui.dialogs import (
    ConfirmationDialog,
    LoadingDialog,
    TraySettingsDialog,
)
from torretray_pi.ui.widgets import ReservationTable


class WorkerSignals(QtCore.QObject):
    succeeded = QtCore.pyqtSignal(object)
    failed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()


class BackgroundTask(QtCore.QRunnable):
    """Run one blocking function on the Qt thread pool."""

    def __init__(self, fn: Callable[[], object]) -> None:
        super().__init__()
        self._fn = fn
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self) -> None:
        try:
            result = self._fn()
        except Exception as exc:  # pragma: no cover - exercised through UI
            self.signals.failed.emit(str(exc))
        else:
            self.signals.succeeded.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QtWidgets.QMainWindow):
    """Main TorreTray operational screen."""

    def __init__(self, *, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.client = BackendClient(
            base_url=settings.api_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.printer = PrinterService(settings)
        self.local_state = LocalReservationStateStore(settings.local_state_db_path)
        self.service = ReservationService(
            client=self.client,
            printer=self.printer,
            local_state=self.local_state,
            now_provider=settings.current_datetime,
        )
        self.thread_pool = QtCore.QThreadPool(self)
        self.loading_dialog: LoadingDialog | None = None
        self._bell_player = BellPlayer(sound_path=settings.bell_sound_path, parent=self)
        self._bell_player.set_muted(settings.bell_muted)
        self._busy = False
        self._snapshot: ReservationSnapshot | None = None
        self._active_service: ScheduledServiceWindow | None = None
        self._active_filters: ReservationFilters | None = None
        self._last_auto_refresh_at: datetime | None = None
        self._schedule_windows: list[ScheduledServiceWindow] = []
        self._schedule_loaded_at: datetime | None = None
        self._next_bell_check_at: datetime | None = None
        self._pending_status_sync_running = False

        self._build_ui()
        self._bind_events()
        self._setup_timers()

        QtCore.QTimer.singleShot(
            250,
            lambda: self._evaluate_schedule(force_refresh=True, show_loading=True),
        )

    def _build_ui(self) -> None:
        self.setWindowTitle("Vassoi Torrescalla")
        self.setWindowIcon(QtGui.QIcon(str(self.settings.window_icon_path)))
        self.resize(1210, 780)

        central_widget = QtWidgets.QWidget(self)
        root_layout = QtWidgets.QHBoxLayout(central_widget)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(6)

        root_layout.addWidget(self._build_table_area(), stretch=4)
        root_layout.addWidget(self._build_control_panel(), stretch=1)

        self.setCentralWidget(central_widget)

        self.status_label = QtWidgets.QLabel("Ultimo aggiornamento: N/D", self)
        self.statusBar().addPermanentWidget(self.status_label)
        self.statusBar().showMessage("In attesa della prima fascia oraria attiva")

    def _build_table_area(self) -> QtWidgets.QWidget:
        wrapper = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QtWidgets.QFrame(wrapper)
        header.setObjectName("tablePanel")
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(2)

        title = QtWidgets.QLabel("Prenotazioni di oggi", header)
        title.setObjectName("panelTitle")
        header_layout.addWidget(title)

        self.context_label = QtWidgets.QLabel("", header)
        self.context_label.setObjectName("contextLabel")
        self.context_label.setWordWrap(True)
        header_layout.addWidget(self.context_label)
        layout.addWidget(header)

        self.pending_table = ReservationTable(
            title="Da stampare:",
            action_icon_path=str(self.settings.printer_icon_path),
            action_tooltip="Stampa ticket",
            secondary_action_icon_path=str(self.settings.cancel_icon_path),
            secondary_action_tooltip="Annulla prenotazione",
            secondary_action_role="danger",
            parent=wrapper,
        )
        self.printed_table = ReservationTable(
            title="Gia stampati:",
            action_icon_path=str(self.settings.printer_icon_path),
            action_tooltip="Ristampa ticket",
            parent=wrapper,
        )
        self.printed_table.setMaximumHeight(360)

        layout.addWidget(self.pending_table, stretch=3)
        layout.addWidget(self.printed_table, stretch=2)
        return wrapper

    def _build_control_panel(self) -> QtWidgets.QFrame:
        panel = QtWidgets.QFrame(self)
        panel.setObjectName("controlPanel")
        panel.setMinimumWidth(270)

        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QtWidgets.QLabel("Comandi:", panel)
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        auto_label = QtWidgets.QLabel("Modalita automatica", panel)
        auto_label.setObjectName("sectionTitle")
        layout.addWidget(auto_label)

        self.mode_description = QtWidgets.QLabel(panel)
        self.mode_description.setObjectName("contextLabel")
        self.mode_description.setWordWrap(True)
        layout.addWidget(self.mode_description)

        layout.addSpacing(10)

        self.print_pending_button = self._make_action_button("Stampa", "primary")
        self.refresh_button = self._make_action_button("Aggiorna", "secondary")
        self.settings_button = self._make_action_button("Impostazioni", "secondary")
        self.reprint_all_button = self._make_action_button("Ristampa", "secondary")

        layout.addWidget(self.print_pending_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.settings_button)
        layout.addStretch()
        layout.addWidget(self.reprint_all_button)

        footer_logo = QtWidgets.QLabel(panel)
        footer_logo.setAlignment(QtCore.Qt.AlignCenter)
        footer_logo.setPixmap(QtGui.QPixmap(str(self.settings.footer_logo_path)))
        layout.addWidget(footer_logo)

        return panel

    def _bind_events(self) -> None:
        self.refresh_button.clicked.connect(self._manual_refresh)
        self.print_pending_button.clicked.connect(self._print_pending_batch)
        self.reprint_all_button.clicked.connect(self._reprint_all_printed)
        self.pending_table.primary_action_requested.connect(self._print_single_pending)
        self.pending_table.secondary_action_requested.connect(self._cancel_single_pending)
        self.printed_table.primary_action_requested.connect(self._reprint_single)
        self.settings_button.clicked.connect(self._open_settings_dialog)

    def _setup_timers(self) -> None:
        self.schedule_timer = QtCore.QTimer(self)
        self.schedule_timer.setInterval(30 * 1000)
        self.schedule_timer.timeout.connect(
            lambda: self._evaluate_schedule(force_refresh=False, show_loading=False)
        )
        self.schedule_timer.start()

        self.bell_timer = QtCore.QTimer(self)
        self.bell_timer.setSingleShot(True)
        self.bell_timer.timeout.connect(self._handle_bell_timer)

    def _make_action_button(self, label: str, variant: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(label, self)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setMinimumHeight(98)
        button.setProperty("variant", variant)
        return button

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
            self._refresh_schedule(force_data_refresh=force_refresh, show_loading=show_loading)
            return

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
        if service_changed:
            self._snapshot = None
            self._last_auto_refresh_at = None
            self.pending_table.set_reservations([])
            self.printed_table.set_reservations([])
            self.status_label.setText("Ultimo aggiornamento: N/D")
        self._sync_bell_scheduler(now, force=service_changed or force_refresh)

        if active_service is None:
            if force_refresh:
                self._refresh_idle_day(show_loading=show_loading)
            else:
                self._apply_idle_state(now)
            return

        self._update_active_context(now, active_service)
        refresh_due = self._last_auto_refresh_at is None or (
            now - self._last_auto_refresh_at
        ).total_seconds() >= self.settings.auto_refresh_minutes * 60

        if force_refresh or service_changed or refresh_due:
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
        self._schedule_windows = sorted(
            schedule_windows,
            key=lambda window: (window.date, window.start_time, window.key),
        )
        self._schedule_loaded_at = self.settings.current_datetime()
        self._continue_after_schedule_refresh(force_data_refresh=force_data_refresh)

    def _apply_manual_schedule_refresh(
        self,
        schedule_windows: list[ScheduledServiceWindow],
    ) -> None:
        self._schedule_windows = sorted(
            schedule_windows,
            key=lambda window: (window.date, window.start_time, window.key),
        )
        self._schedule_loaded_at = self.settings.current_datetime()
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
        if service_changed:
            self._snapshot = None
            self._last_auto_refresh_at = None
            self.pending_table.set_reservations([])
            self.printed_table.set_reservations([])
            self.status_label.setText("Ultimo aggiornamento: N/D")
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
        self._snapshot = snapshot
        self._last_auto_refresh_at = snapshot.refreshed_at
        self.pending_table.set_reservations(snapshot.unprinted)
        self.printed_table.set_reservations(snapshot.printed)

        if self._active_service is not None:
            self._update_active_context(snapshot.refreshed_at, self._active_service)

        self.status_label.setText(
            f"Ultimo aggiornamento: {snapshot.refreshed_at.strftime('%d/%m/%Y %H:%M:%S')}"
        )
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
        self.pending_table.set_reservations([])
        self.printed_table.set_reservations([])
        if refreshed_at is None:
            self.status_label.setText("Ultimo aggiornamento: N/D")
        else:
            self.status_label.setText(
                f"Ultimo aggiornamento: {refreshed_at.strftime('%d/%m/%Y %H:%M:%S')}"
            )

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
                "L'app carica automaticamente i ticket "
                f"{self.settings.loading_time_before_meal} minuti prima del pasto, "
                f"li aggiorna ogni {self.settings.auto_refresh_minutes} minuti "
                f"e controlla la campanella ogni {self.settings.bell_interval_seconds} secondi "
                f"a partire da {self.settings.bell_time_before_meal} minuti prima del pasto."
            )
        self.statusBar().showMessage("Fuori fascia oraria automatica", 3000)
        self._refresh_action_states()

    def _update_active_context(
        self,
        current_moment: datetime,
        active_service: ScheduledServiceWindow,
    ) -> None:
        bell_start = self._bell_window_starts_at(active_service)
        if current_moment < active_service.starts_at():
            phase_label = "Precaricamento attivo"
        else:
            phase_label = "Fascia attiva"

        self.context_label.setText(
            f"{phase_label}: {active_service.label} fino alle "
            f"{active_service.end_time.strftime('%H:%M')}."
        )
        self.mode_description.setText(
            f"Ticket caricati {self.settings.loading_time_before_meal} minuti prima del pasto, "
            f"refresh ogni {self.settings.auto_refresh_minutes} minuti e campanella da "
            f"{bell_start.strftime('%H:%M')} ogni {self.settings.bell_interval_seconds} secondi "
            "se restano ticket da stampare."
        )

    def _refresh_action_states(self) -> None:
        pending = bool(self._snapshot and self._snapshot.unprinted)
        printed = bool(self._snapshot and self._snapshot.printed)
        self.print_pending_button.setEnabled(pending and not self._busy)
        self.reprint_all_button.setEnabled(printed and not self._busy)
        self.refresh_button.setEnabled(not self._busy)
        self.settings_button.setEnabled(not self._busy)

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

    def _on_print_success(self, result: PrintJobResult) -> None:
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
        result: StatusUpdateResult,
    ) -> None:
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
            self.pending_table.set_reservations(self._snapshot.unprinted)
            self.printed_table.set_reservations(self._snapshot.printed)
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
        self.pending_table.set_reservations(self._snapshot.unprinted)
        self.printed_table.set_reservations(self._snapshot.printed)
        self._refresh_action_states()

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
            int(
                (self._next_bell_check_at - reference_time).total_seconds() * 1000
            ),
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

    def _run_task(
        self,
        *,
        task: Callable[[], object],
        on_success: Callable[[object], None],
        loading_message: str | None,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        self._busy = True
        self._refresh_action_states()

        if loading_message:
            self.loading_dialog = LoadingDialog(
                message=loading_message,
                gif_path=str(self.settings.loading_gif_path),
                parent=self,
            )
            self.loading_dialog.show()

        worker = BackgroundTask(task)
        worker.signals.succeeded.connect(on_success)
        worker.signals.failed.connect(self._handle_worker_error)
        worker.signals.finished.connect(self._finish_background_task)
        if on_finished is not None:
            worker.signals.finished.connect(on_finished)
        self.thread_pool.start(worker)

    def _run_background_task(
        self,
        *,
        task: Callable[[], object],
        on_success: Callable[[object], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        worker = BackgroundTask(task)
        if on_success is not None:
            worker.signals.succeeded.connect(on_success)
        if on_error is not None:
            worker.signals.failed.connect(on_error)
        if on_finished is not None:
            worker.signals.finished.connect(on_finished)
        self.thread_pool.start(worker)

    def _sync_pending_status_updates_in_background(self) -> None:
        if self._busy or self._pending_status_sync_running:
            return
        if not self.service.has_pending_status_sync():
            return

        self._pending_status_sync_running = True
        self._run_background_task(
            task=self.service.sync_pending_status_updates,
            on_success=self._handle_pending_status_sync_result,
            on_finished=self._finish_pending_status_sync,
        )

    def _handle_pending_status_sync_result(self, synced_count: object) -> None:
        if not isinstance(synced_count, int) or synced_count <= 0:
            return
        self.statusBar().showMessage(
            f"Sincronizzati {synced_count} aggiornamenti locali con il backend.",
            5000,
        )

    def _finish_pending_status_sync(self) -> None:
        self._pending_status_sync_running = False

    def _finish_background_task(self) -> None:
        self._busy = False
        self._refresh_action_states()
        if self.loading_dialog is not None:
            self.loading_dialog.accept()
            self.loading_dialog = None

    def _handle_worker_error(self, message: str) -> None:
        safe_message = message or "Si e verificato un errore inatteso."
        self.statusBar().showMessage(safe_message, 6000)

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
