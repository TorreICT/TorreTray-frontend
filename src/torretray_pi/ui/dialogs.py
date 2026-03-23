from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets


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
