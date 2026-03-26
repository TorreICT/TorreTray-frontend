from __future__ import annotations

from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.audio import BellPlayer
from torretray_pi.backend_client import BackendClient
from torretray_pi.config import AppSettings, ScheduledServiceWindow
from torretray_pi.local_state import LocalReservationStateStore
from torretray_pi.models import ReservationFilters
from torretray_pi.printing import PrinterService
from torretray_pi.services import ReservationService, ReservationSnapshot
from torretray_pi.ui.main_window_actions import MainWindowActionMixin
from torretray_pi.ui.main_window_schedule import MainWindowScheduleMixin
from torretray_pi.ui.main_window_tasks import MainWindowTaskMixin
from torretray_pi.ui.main_window_ui import MainWindowUiMixin


class MainWindow(
    QtWidgets.QMainWindow,
    MainWindowUiMixin,
    MainWindowScheduleMixin,
    MainWindowActionMixin,
    MainWindowTaskMixin,
):
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
        self.thread_pool.setMaxThreadCount(2)
        self.loading_dialog: QtWidgets.QDialog | None = None
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
        self._backend_connection_down = False

        self._build_ui()
        self._bind_events()
        self._setup_timers()

        QtCore.QTimer.singleShot(
            250,
            lambda: self._evaluate_schedule(force_refresh=True, show_loading=True),
        )

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.schedule_timer.stop()
        self.bell_timer.stop()
        if self.loading_dialog is not None:
            self.loading_dialog.close()
            self.loading_dialog = None
        self.thread_pool.waitForDone(3000)
        super().closeEvent(event)
