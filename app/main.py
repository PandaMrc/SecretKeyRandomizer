"""Desktop entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.theme import dark_theme_stylesheet  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SecretKeyRandomizer")
    app.setStyleSheet(dark_theme_stylesheet())

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
