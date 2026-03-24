from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.config import AppSettings
from torretray_pi.printing import TicketPreview


class ConfirmationDialog(QtWidgets.QDialog):
    """Simple confirmation dialog used for print actions."""

    def __init__(
        self,
        *,
        title: str,
        message: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.resize(430, 170)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QtWidgets.QLabel(message, self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok,
            parent=self,
        )
        buttons.setCenterButtons(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class LoadingDialog(QtWidgets.QDialog):
    """Modal loading dialog used during refresh and print operations."""

    def __init__(
        self,
        *,
        message: str,
        gif_path: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.SplashScreen)
        self.setWindowTitle(" ")
        self.resize(380, 120)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self._message_label = QtWidgets.QLabel(message, self)
        self._message_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._message_label)

        self._spinner_label = QtWidgets.QLabel(self)
        self._spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._spinner_label)

        self._movie = QtGui.QMovie(gif_path)
        self._movie.setScaledSize(QtCore.QSize(34, 34))
        self._spinner_label.setMovie(self._movie)
        self._movie.start()


class TicketPreviewDialog(QtWidgets.QDialog):
    """Render a visual preview of a ticket without sending it to the printer."""

    def __init__(
        self,
        *,
        ticket: TicketPreview,
        logo_path: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Anteprima ticket")
        self.resize(420, 720)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(12)

        ticket_frame = QtWidgets.QFrame(self)
        ticket_frame.setObjectName("tablePanel")
        ticket_layout = QtWidgets.QVBoxLayout(ticket_frame)
        ticket_layout.setContentsMargins(28, 28, 28, 28)
        ticket_layout.setSpacing(10)

        logo_label = QtWidgets.QLabel(ticket_frame)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_label.setMinimumHeight(72)
        logo_label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        logo_pixmap = QtGui.QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    170,
                    56,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            )
        ticket_layout.addWidget(logo_label)

        title_label = QtWidgets.QLabel(ticket.title, ticket_frame)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_font = title_label.font()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        ticket_layout.addWidget(title_label)

        for text in (ticket.meal_line, ticket.printed_at_line):
            label = QtWidgets.QLabel(text, ticket_frame)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setWordWrap(True)
            ticket_layout.addWidget(label)

        ticket_layout.addSpacing(8)

        name_label = QtWidgets.QLabel(ticket.name, ticket_frame)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_font = name_label.font()
        name_font.setPointSize(18)
        name_font.setBold(True)
        name_label.setFont(name_font)
        ticket_layout.addWidget(name_label)

        if ticket.diet_label:
            diet_label = QtWidgets.QLabel(ticket.diet_label, ticket_frame)
            diet_label.setAlignment(QtCore.Qt.AlignCenter)
            diet_label.setWordWrap(True)
            ticket_layout.addWidget(diet_label)

        ticket_layout.addSpacing(12)

        section_label = QtWidgets.QLabel("Preferenze:", ticket_frame)
        section_font = section_label.font()
        section_font.setBold(True)
        section_label.setFont(section_font)
        ticket_layout.addWidget(section_label)

        for line in ticket.preference_lines:
            preference_label = QtWidgets.QLabel(line, ticket_frame)
            preference_label.setWordWrap(True)
            ticket_layout.addWidget(preference_label)

        ticket_layout.addStretch()
        root_layout.addWidget(ticket_frame)

        note_label = QtWidgets.QLabel(
            "Anteprima visiva del layout. Il risultato finale puo variare leggermente sulla stampante termica.",
            self,
        )
        note_label.setWordWrap(True)
        note_label.setAlignment(QtCore.Qt.AlignCenter)
        root_layout.addWidget(note_label)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close, parent=self)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        root_layout.addWidget(buttons)


class TraySettingsDialog(QtWidgets.QDialog):
    """Dialog used on-site to edit local tray runtime settings."""

    def __init__(
        self,
        *,
        settings: AppSettings,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Impostazioni locali")
        self.resize(460, 340)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        intro_label = QtWidgets.QLabel(
            (
                "Modifica i tempi operativi locali dell'app. "
                "Le modifiche vengono salvate nel file .env del tray app."
            ),
            self,
        )
        intro_label.setWordWrap(True)
        root_layout.addWidget(intro_label)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.setFormAlignment(QtCore.Qt.AlignTop)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(12)

        self.auto_refresh_spin = self._build_spinbox(
            value=settings.auto_refresh_minutes,
            minimum=1,
            maximum=120,
            suffix=" min",
        )
        self.preload_spin = self._build_spinbox(
            value=settings.preload_minutes,
            minimum=0,
            maximum=120,
            suffix=" min",
        )
        self.lookahead_spin = self._build_spinbox(
            value=settings.schedule_lookahead_days,
            minimum=1,
            maximum=30,
            suffix=" giorni",
        )
        self.bell_interval_spin = self._build_spinbox(
            value=settings.bell_interval_seconds,
            minimum=15,
            maximum=3600,
            suffix=" sec",
            step=15,
        )
        self.bell_muted_checkbox = QtWidgets.QCheckBox("Disattiva campanella")
        self.bell_muted_checkbox.setChecked(settings.bell_muted)

        form_layout.addRow("Refresh automatico", self.auto_refresh_spin)
        form_layout.addRow("Precaricamento", self.preload_spin)
        form_layout.addRow("Orizzonte schedule", self.lookahead_spin)
        form_layout.addRow("Intervallo campanella", self.bell_interval_spin)
        form_layout.addRow("Audio campanella", self.bell_muted_checkbox)
        root_layout.addLayout(form_layout)
        root_layout.addStretch()

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root_layout.addWidget(buttons)

    def values(self) -> dict[str, int]:
        """Return the settings chosen by the operator."""
        return {
            "auto_refresh_minutes": self.auto_refresh_spin.value(),
            "preload_minutes": self.preload_spin.value(),
            "schedule_lookahead_days": self.lookahead_spin.value(),
            "bell_interval_seconds": self.bell_interval_spin.value(),
            "bell_muted": self.bell_muted_checkbox.isChecked(),
        }

    @staticmethod
    def _build_spinbox(
        *,
        value: int,
        minimum: int,
        maximum: int,
        suffix: str,
        step: int = 1,
    ) -> QtWidgets.QSpinBox:
        spinbox = QtWidgets.QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setSingleStep(step)
        spinbox.setValue(value)
        spinbox.setSuffix(suffix)
        spinbox.setMinimumHeight(42)
        return spinbox
