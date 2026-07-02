from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def test_ui_tabs_render_and_generation_flows(qt_app: QApplication) -> None:
    window = MainWindow()

    assert window.tabs.count() == 3
    assert window.tabs.tabText(0) == "Single"
    assert window.tabs.tabText(1) == "Bulk .env"
    assert window.tabs.tabText(2) == "Template Packs"

    window.generate_single()
    assert window._current_batch is not None
    assert len(window._current_batch.secrets) == 1

    window.generate_bulk()
    assert window._current_batch is not None
    assert len(window._current_batch.secrets) >= 1

    window.generate_template()
    assert window._current_batch is not None
    assert len(window._current_batch.secrets) >= 1


def test_clipboard_delay_options_render(qt_app: QApplication) -> None:
    window = MainWindow()

    assert [window.clear_delay_combo.itemData(index) for index in range(window.clear_delay_combo.count())] == [
        10,
        30,
        60,
    ]


def test_masked_output_is_default(qt_app: QApplication) -> None:
    window = MainWindow()
    window.generate_single()
    generated = window._current_batch.first()

    assert generated is not None
    assert not window.reveal_checkbox.isChecked()
    assert generated.value not in window.output_area.toPlainText()
