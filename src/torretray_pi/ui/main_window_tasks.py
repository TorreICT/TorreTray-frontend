from __future__ import annotations

from collections.abc import Callable

from PyQt5 import QtCore

from torretray_pi.ui.dialogs import LoadingDialog


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


class MainWindowTaskMixin:
    """Background-task helpers shared by the main window workflows."""

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
        self._set_backend_connection_down(False)
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
            self.loading_dialog.close()
            self.loading_dialog = None

    def _handle_worker_error(self, message: str) -> None:
        safe_message = message or "Si e verificato un errore inatteso."
        if self._is_backend_connection_error(safe_message):
            self._set_backend_connection_down(True)
        self.statusBar().showMessage(safe_message, 6000)

    def _is_backend_connection_error(self, message: str) -> bool:
        normalized = message.strip().lower()
        return "impossibile contattare il backend" in normalized

    def _set_backend_connection_down(self, is_down: bool) -> None:
        if self._backend_connection_down == is_down:
            return
        self._backend_connection_down = is_down
        self.connection_banner.setVisible(is_down)
