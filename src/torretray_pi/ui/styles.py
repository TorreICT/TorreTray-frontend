from __future__ import annotations

from PyQt5 import QtWidgets


APP_STYLESHEET = """
QMainWindow {
    background: #0f0f10;
}
QWidget {
    color: #f3f3f1;
    font-family: "DejaVu Sans";
    font-size: 12pt;
}
QFrame#controlPanel, QFrame#tablePanel {
    background: #18191c;
    border: 1px solid #2f3136;
    border-radius: 18px;
}
QDialog {
    background: #17181b;
    border: 1px solid #343840;
    border-radius: 18px;
}
QDialog QLabel {
    color: #f3f3f1;
}
QLabel#panelTitle {
    font-size: 16pt;
    font-weight: 700;
    color: #f3f3f1;
}
QLabel#sectionTitle {
    font-size: 14pt;
    font-weight: 700;
    color: #d9dce2;
}
QLabel#contextLabel {
    font-size: 11pt;
    color: #b9bcc3;
}
QPushButton {
    min-height: 48px;
    border-radius: 14px;
    border: 1px solid #3b3e45;
    background: #23252a;
    padding: 10px 14px;
    font-weight: 700;
    color: #f3f3f1;
}
QPushButton:hover {
    border-color: #ffd84d;
    background: #2a2d33;
}
QPushButton:disabled {
    color: #7e8188;
    background: #1a1b1f;
    border-color: #2b2d33;
}
QPushButton[variant="primary"] {
    background: #ffd84d;
    color: #141414;
    border-color: #ffd84d;
}
QPushButton[variant="secondary"] {
    background: #2a2d33;
    color: #f6f6f4;
    border-color: #454952;
}
QPushButton[variant="filter"] {
    background: #202227;
    color: #d7d9de;
}
QPushButton[variant="filter"]:checked {
    background: #ffd84d;
    color: #141414;
    border-color: #ffd84d;
}
QPushButton[compact="true"] {
    min-height: 32px;
    min-width: 32px;
    max-height: 32px;
    max-width: 48px;
    padding: 4px;
    border-radius: 10px;
}
QDialogButtonBox QPushButton {
    min-height: 38px;
    max-height: 38px;
    min-width: 110px;
    padding: 8px 14px;
    border-radius: 12px;
}
QSpinBox {
    min-height: 42px;
    border-radius: 12px;
    border: 1px solid #3b3e45;
    background: #23252a;
    padding: 6px 12px;
    color: #f3f3f1;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 28px;
    border: 0;
    background: #2b2e34;
    border-radius: 8px;
    margin: 4px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #343840;
}
QCheckBox {
    spacing: 12px;
}
QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 1px solid #3b3e45;
    background: #23252a;
}
QCheckBox::indicator:checked {
    background: #ffd84d;
    border-color: #ffd84d;
}
QTableWidget {
    background: #121316;
    alternate-background-color: #191b20;
    border: 1px solid #2e3138;
    border-radius: 16px;
    gridline-color: #252830;
    selection-background-color: #3a3d45;
    color: #f3f3f1;
    outline: 0;
}
QHeaderView::section {
    background: #1f2126;
    color: #f3f3f1;
    border: 0;
    border-bottom: 1px solid #343840;
    padding: 12px 8px;
    font-weight: 700;
}
QTableWidget::item {
    padding: 16px 14px;
}
QScrollBar:vertical {
    background: #16181c;
    width: 34px;
    margin: 2px;
    border-radius: 12px;
}
QScrollBar::handle:vertical {
    background: #5e6168;
    min-height: 30px;
    border-radius: 12px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QStatusBar {
    background: #121316;
    color: #f3f3f1;
}
"""


def apply_app_style(app: QtWidgets.QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
