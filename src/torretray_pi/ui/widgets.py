from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets

from torretray_pi.models import Reservation


class ReservationTable(QtWidgets.QFrame):
    """Reusable table card for reservation lists."""

    row_action_requested = QtCore.pyqtSignal(object)

    def __init__(
        self,
        *,
        title: str,
        action_icon_path: str,
        action_tooltip: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._action_icon = QtGui.QIcon(action_icon_path)
        self._action_tooltip = action_tooltip

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
        self.table.setColumnWidth(1, 72)
        layout.addWidget(self.table)

    def set_reservations(self, reservations: list[Reservation]) -> None:
        self.table.setRowCount(len(reservations))
        for row, reservation in enumerate(reservations):
            self._set_row(row, reservation)

    def _set_row(self, row: int, reservation: Reservation) -> None:
        name_item = QtWidgets.QTableWidgetItem(reservation.name)
        self.table.setItem(row, 0, name_item)

        button = QtWidgets.QPushButton(self.table)
        button.setIcon(self._action_icon)
        button.setToolTip(self._action_tooltip)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setProperty("compact", "true")
        button.setIconSize(QtCore.QSize(18, 18))
        button.clicked.connect(
            lambda _checked=False, item=reservation: self.row_action_requested.emit(item)
        )
        self.table.setCellWidget(row, 1, button)
        self.table.setRowHeight(row, 64)
