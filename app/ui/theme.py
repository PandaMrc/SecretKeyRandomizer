"""Application theme."""

from __future__ import annotations


def dark_theme_stylesheet() -> str:
    return """
    QWidget {
        background: #111418;
        color: #e7edf3;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 13px;
    }
    QMainWindow {
        background: #111418;
    }
    QLabel#Title {
        font-size: 24px;
        font-weight: 700;
        color: #f5f8fb;
    }
    QLabel#Subtitle {
        color: #aab6c4;
        line-height: 1.3;
    }
    QLabel#CardTitle {
        font-size: 13px;
        font-weight: 700;
        color: #f5f8fb;
    }
    QLabel#MetricValue {
        font-size: 22px;
        font-weight: 700;
        color: #6ee7b7;
    }
    QLabel#Warning {
        color: #f8d66d;
        background: #292318;
        border: 1px solid #4b3f1e;
        border-radius: 6px;
        padding: 10px;
    }
    QLabel#ClipboardWarning {
        color: #aab6c4;
    }
    QFrame#Card {
        background: #171b21;
        border: 1px solid #29313a;
        border-radius: 8px;
    }
    QLineEdit, QSpinBox, QComboBox, QPlainTextEdit {
        background: #0d1014;
        border: 1px solid #33404d;
        border-radius: 6px;
        color: #eef3f8;
        padding: 8px;
        selection-background-color: #2563eb;
    }
    QPlainTextEdit {
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 13px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        width: 18px;
    }
    QPushButton {
        background: #2563eb;
        border: 1px solid #3b82f6;
        border-radius: 6px;
        color: #ffffff;
        font-weight: 700;
        padding: 9px 14px;
    }
    QPushButton:hover {
        background: #1d4ed8;
    }
    QPushButton:pressed {
        background: #1e40af;
    }
    QPushButton:disabled {
        background: #29313a;
        border-color: #33404d;
        color: #768393;
    }
    QCheckBox {
        color: #d4dde8;
        spacing: 8px;
    }
    QStatusBar {
        background: #111418;
        color: #aab6c4;
    }
    """
