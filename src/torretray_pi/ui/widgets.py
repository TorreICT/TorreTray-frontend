from __future__ import annotations

from collections.abc import Callable

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.models import Reservation


class ReservationTable(QtWidgets.QFrame):
    """Reusable table card for reservation lists."""

    primary_action_requested = QtCore.pyqtSignal(object)
    secondary_action_requested = QtCore.pyqtSignal(object)

    def __init__(
        self,
        *,
        title: str,
        action_icon_path: str,
        action_tooltip: str,
        secondary_action_icon_path: str | None = None,
        secondary_action_tooltip: str | None = None,
        secondary_action_role: str = "secondary",
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._action_icon = QtGui.QIcon(action_icon_path)
        self._action_tooltip = action_tooltip
        self._secondary_action_icon = (
            QtGui.QIcon(secondary_action_icon_path)
            if secondary_action_icon_path is not None
            else None
        )
        self._secondary_action_tooltip = secondary_action_tooltip
        self._secondary_action_role = secondary_action_role

        self.setObjectName("tablePanel")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.title_label = QtWidgets.QLabel(title, self)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nome", ""])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(1, 148 if self._secondary_action_icon else 92)
        layout.addWidget(self.table)

    def set_reservations(self, reservations: list[Reservation]) -> None:
        self.table.setRowCount(len(reservations))
        for row, reservation in enumerate(reservations):
            self._set_row(row, reservation)

    def _set_row(self, row: int, reservation: Reservation) -> None:
        name_wrapper = QtWidgets.QWidget(self.table)
        name_wrapper.setObjectName("reservationNameCell")
        name_layout = QtWidgets.QHBoxLayout(name_wrapper)
        name_layout.setContentsMargins(18, 0, 12, 0)
        name_layout.setSpacing(0)
        name_layout.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

        name_label = QtWidgets.QLabel(reservation.name, name_wrapper)
        name_label.setObjectName("reservationNameLabel")
        name_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        name_layout.addWidget(name_label)
        self.table.setCellWidget(row, 0, name_wrapper)

        button_wrapper = QtWidgets.QWidget(self.table)
        button_wrapper.setObjectName("reservationActionCell")
        wrapper_layout = QtWidgets.QVBoxLayout(button_wrapper)
        wrapper_layout.setContentsMargins(6, 6, 6, 6)
        wrapper_layout.setSpacing(0)
        wrapper_layout.setAlignment(QtCore.Qt.AlignVCenter)

        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)

        actions_layout.addWidget(
            self._build_action_button(
                parent=button_wrapper,
                icon=self._action_icon,
                tooltip=self._action_tooltip,
                role="primary",
                callback=lambda: self.primary_action_requested.emit(reservation),
            )
        )
        if self._secondary_action_icon is not None and self._secondary_action_tooltip:
            actions_layout.addWidget(
                self._build_action_button(
                    parent=button_wrapper,
                    icon=self._secondary_action_icon,
                    tooltip=self._secondary_action_tooltip,
                    role=self._secondary_action_role,
                    callback=lambda: self.secondary_action_requested.emit(reservation),
                )
            )

        wrapper_layout.addLayout(actions_layout)
        self.table.setCellWidget(row, 1, button_wrapper)
        self.table.setRowHeight(row, 76)

    @staticmethod
    def _build_action_button(
        *,
        parent: QtWidgets.QWidget,
        icon: QtGui.QIcon,
        tooltip: str,
        role: str,
        callback: Callable[[], None],
    ) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(parent)
        button.setIcon(icon)
        button.setToolTip(tooltip)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setProperty("compact", "true")
        button.setProperty("actionRole", role)
        button.setIconSize(QtCore.QSize(22, 22))
        button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        button.clicked.connect(lambda _checked=False: callback())
        return button
