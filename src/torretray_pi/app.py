from __future__ import annotations

import sys

from PyQt5 import QtGui, QtWidgets

from torretray_pi.config import load_settings
from torretray_pi.ui.main_window import MainWindow
from torretray_pi.ui.styles import apply_app_style


def run() -> int:
    """Start the Qt application."""
    settings = load_settings()

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("TorreTray")
    app.setWindowIcon(QtGui.QIcon(str(settings.window_icon_path)))
    apply_app_style(app)

    window = MainWindow(settings=settings)
    if settings.start_fullscreen:
        window.showFullScreen()
    else:
        window.show()
    return app.exec_()
