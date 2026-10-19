from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.ui.widgets import ReservationTable


class MainWindowUiMixin:
    """Build and wire the main-window widgets."""

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
        layout.addWidget(self._build_connection_banner(panel))
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

    def _build_connection_banner(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        banner = QtWidgets.QFrame(parent)
        banner.setObjectName("connectionBanner")
        banner.hide()

        layout = QtWidgets.QHBoxLayout(banner)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.connection_icon_label = QtWidgets.QLabel(banner)
        warning_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning)
        self.connection_icon_label.setPixmap(warning_icon.pixmap(30, 30))
        self.connection_icon_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.connection_status_label = QtWidgets.QLabel("Lost connection", banner)
        self.connection_status_label.setObjectName("connectionBannerText")

        layout.addWidget(self.connection_icon_label, alignment=QtCore.Qt.AlignTop)
        layout.addWidget(self.connection_status_label, stretch=1)
        self.connection_banner = banner
        return banner
