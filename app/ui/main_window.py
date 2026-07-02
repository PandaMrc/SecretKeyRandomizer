"""Main PySide6 window for SecretKeyRandomizer."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.display import mask_secret
from app.core.formatters import format_env, format_env_block, format_generated_json, format_json_array
from app.core.generator import (
    ASCII_SAFE_CHARSET,
    generate_batch,
    generate_from_request,
    generate_template_pack,
    request_from_preset,
)
from app.core.models import GeneratedSecret, GenerationBatch, GenerationRequest
from app.core.presets import PRESETS, TEMPLATE_PACKS, SecretPreset
from app.core.validators import normalize_encoding, normalize_output_format, validate_env_name
from app.ui.widgets import MetricCard


ENCODINGS = [
    ("hex", "Hex"),
    ("base64", "Base64"),
    ("base64url", "Base64URL"),
    ("ascii-safe", "ASCII-safe"),
    ("custom-charset", "Custom charset"),
    ("uuid-v4", "UUID-v4"),
]

OUTPUT_FORMATS = [
    ("plain", "Value only"),
    ("env", ".env"),
    ("json", "JSON"),
]

DEFAULT_CUSTOM_CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
CLIPBOARD_WARNING = "Clipboard is not secure storage. Copied secrets can be read by other applications."


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SecretKeyRandomizer")
        self.resize(1120, 760)

        self._current_batch: GenerationBatch | None = None
        self._current_output = ""
        self._last_clipboard_text = ""

        self.tabs = QTabWidget()
        self.single_widgets: dict[str, object] = {}
        self.bulk_checks: dict[str, QCheckBox] = {}
        self.template_combo = QComboBox()

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(220)

        self.reveal_checkbox = QCheckBox("Reveal secrets")
        self.reveal_checkbox.setChecked(False)
        self.copy_value_button = QPushButton("Copy value")
        self.copy_env_button = QPushButton("Copy env line")
        self.copy_all_button = QPushButton("Copy all")
        self.clear_clipboard_button = QPushButton("Clear clipboard")
        self.clear_delay_combo = QComboBox()
        for seconds in (10, 30, 60):
            self.clear_delay_combo.addItem(f"{seconds}s", seconds)
        self.clear_delay_combo.setCurrentIndex(1)

        self.entropy_card = MetricCard("Entropy", "-")
        self.security_card = MetricCard("Security Level", "-")
        self.warning_label = QLabel("")
        self.warning_label.setObjectName("Warning")
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()

        self._build_layout()
        self._connect_signals()
        self._apply_single_preset()
        self._set_copy_enabled(False)

    def _build_layout(self) -> None:
        root = QWidget()
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(22, 18, 22, 16)
        main_layout.setSpacing(16)

        title = QLabel("SecretKeyRandomizer")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Generate high-entropy secrets with CSPRNG-backed randomness. "
            "No secret history, telemetry, network access, or storage."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        content_layout = QGridLayout()
        content_layout.setHorizontalSpacing(16)
        content_layout.setVerticalSpacing(16)

        self.tabs.addTab(self._build_single_tab(), "Single")
        self.tabs.addTab(self._build_bulk_tab(), "Bulk .env")
        self.tabs.addTab(self._build_template_tab(), "Template Packs")

        output_card = self._card()
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(16, 14, 16, 14)
        output_layout.setSpacing(10)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.reveal_checkbox)
        action_layout.addStretch(1)
        action_layout.addWidget(QLabel("Clear after"))
        action_layout.addWidget(self.clear_delay_combo)
        output_layout.addLayout(action_layout)
        output_layout.addWidget(self.output_area)

        copy_layout = QHBoxLayout()
        copy_layout.addWidget(self.copy_value_button)
        copy_layout.addWidget(self.copy_env_button)
        copy_layout.addWidget(self.copy_all_button)
        copy_layout.addWidget(self.clear_clipboard_button)
        copy_layout.addStretch(1)
        output_layout.addLayout(copy_layout)

        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.entropy_card)
        metrics_layout.addWidget(self.security_card)
        output_layout.addLayout(metrics_layout)
        output_layout.addWidget(self.warning_label)

        clipboard_label = QLabel(CLIPBOARD_WARNING)
        clipboard_label.setObjectName("ClipboardWarning")
        clipboard_label.setWordWrap(True)
        output_layout.addWidget(clipboard_label)

        content_layout.addWidget(self.tabs, 0, 0)
        content_layout.addWidget(output_card, 0, 1)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        main_layout.addLayout(content_layout)

        self.setCentralWidget(root)
        self.statusBar().showMessage("Ready")

    def _build_single_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        form_card = self._card()
        form = QFormLayout(form_card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        preset_combo = QComboBox()
        for preset in PRESETS.values():
            preset_combo.addItem(f"{preset.name} · {preset.category}", preset.key)
        encoding_combo = QComboBox()
        for value, label in ENCODINGS:
            encoding_combo.addItem(label, value)
        length_input = QSpinBox()
        length_input.setRange(1, 4096)
        prefix_input = QLineEdit()
        suffix_input = QLineEdit()
        env_name_input = QLineEdit()
        custom_charset_input = QLineEdit(DEFAULT_CUSTOM_CHARSET)
        output_format_combo = QComboBox()
        for value, label in OUTPUT_FORMATS:
            output_format_combo.addItem(label, value)
        output_format_combo.setCurrentIndex(1)
        generate_button = QPushButton("Generate")

        self.single_widgets = {
            "preset": preset_combo,
            "encoding": encoding_combo,
            "length": length_input,
            "prefix": prefix_input,
            "suffix": suffix_input,
            "env": env_name_input,
            "charset": custom_charset_input,
            "format": output_format_combo,
            "generate": generate_button,
        }

        form.addRow("Preset", preset_combo)
        form.addRow("Encoding", encoding_combo)
        form.addRow("Bytes / chars", length_input)
        form.addRow("Prefix", prefix_input)
        form.addRow("Suffix", suffix_input)
        form.addRow("ENV name", env_name_input)
        form.addRow("Custom charset", custom_charset_input)
        form.addRow("Output format", output_format_combo)

        layout.addWidget(form_card)
        layout.addWidget(generate_button)
        layout.addStretch(1)
        return widget

    def _build_bulk_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        info = QLabel("Select any presets and generate a complete .env block.")
        info.setWordWrap(True)
        layout.addWidget(info)

        grid_card = self._card()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        for index, preset in enumerate(PRESETS.values()):
            checkbox = QCheckBox(f"{preset.name} ({preset.env_name})")
            checkbox.setChecked(preset.key in {"jwt", "api_key", "webhook", "database_encryption"})
            self.bulk_checks[preset.key] = checkbox
            grid.addWidget(checkbox, index // 2, index % 2)

        generate_button = QPushButton("Generate bulk .env")
        generate_button.clicked.connect(self.generate_bulk)
        layout.addWidget(grid_card)
        layout.addWidget(generate_button)
        layout.addStretch(1)
        return widget

    def _build_template_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        form_card = self._card()
        form = QFormLayout(form_card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        for key, (name, preset_keys) in TEMPLATE_PACKS.items():
            self.template_combo.addItem(f"{name} · {len(preset_keys)} secrets", key)
        generate_button = QPushButton("Generate template pack")
        generate_button.clicked.connect(self.generate_template)

        form.addRow("Template", self.template_combo)
        layout.addWidget(form_card)
        layout.addWidget(generate_button)
        layout.addStretch(1)
        return widget

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _connect_signals(self) -> None:
        self._single("preset").currentIndexChanged.connect(self._apply_single_preset)
        self._single("encoding").currentIndexChanged.connect(self._sync_single_encoding)
        self._single("generate").clicked.connect(self.generate_single)
        self.reveal_checkbox.stateChanged.connect(self._refresh_output)
        self.copy_value_button.clicked.connect(self.copy_value)
        self.copy_env_button.clicked.connect(self.copy_env_line)
        self.copy_all_button.clicked.connect(self.copy_all)
        self.clear_clipboard_button.clicked.connect(self.clear_clipboard)

    def _apply_single_preset(self, _index: int | None = None) -> None:
        preset = self._selected_single_preset()
        self._single("env").setText(preset.env_name)
        self._single("length").setValue(preset.byte_length)
        self._single("prefix").setText(preset.prefix)
        self._single("suffix").setText(preset.suffix)
        self._set_combo_value(self._single("encoding"), preset.encoding)
        self._sync_single_encoding()
        self._set_warning(preset.warning)

    def _sync_single_encoding(self) -> None:
        encoding = self._selected_single_encoding()
        self._single("charset").setEnabled(encoding == "custom-charset")
        self._single("length").setEnabled(encoding != "uuid-v4")

    def generate_single(self) -> None:
        try:
            request = self._single_request()
            generated = generate_from_request(request)
            self._set_batch(GenerationBatch("Single Secret", (generated,)), request.output_format)
            self.statusBar().showMessage("Generated single secret")
        except Exception as exc:
            self._show_error(str(exc))

    def generate_bulk(self) -> None:
        selected = [key for key, checkbox in self.bulk_checks.items() if checkbox.isChecked()]
        if not selected:
            self._show_error("Select at least one preset.")
            return
        try:
            requests = [request_from_preset(key, output_format="env") for key in selected]
            self._set_batch(generate_batch("Bulk .env", requests), "env")
            self.statusBar().showMessage("Generated bulk .env")
        except Exception as exc:
            self._show_error(str(exc))

    def generate_template(self) -> None:
        try:
            template_key = str(self.template_combo.currentData())
            self._set_batch(generate_template_pack(template_key, output_format="env"), "env")
            self.statusBar().showMessage("Generated template pack")
        except Exception as exc:
            self._show_error(str(exc))

    def copy_value(self) -> None:
        generated = self._first_generated()
        if generated:
            self._copy_text(generated.value)

    def copy_env_line(self) -> None:
        generated = self._first_generated()
        if generated:
            self._copy_text(format_env(generated.env_name, generated.value))

    def copy_all(self) -> None:
        if self._current_output:
            self._copy_text(self._current_output)

    def clear_clipboard(self) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.clear()
        self._last_clipboard_text = ""
        self.statusBar().showMessage("Clipboard cleared")

    def closeEvent(self, event) -> None:  # noqa: N802
        clipboard = QGuiApplication.clipboard()
        if self._last_clipboard_text and clipboard.text() == self._last_clipboard_text:
            clipboard.clear()
        super().closeEvent(event)

    def _single_request(self) -> GenerationRequest:
        env_name = self._single("env").text().strip()
        validate_env_name(env_name)
        byte_length = int(self._single("length").value())
        encoding = self._selected_single_encoding()
        return request_from_preset(
            self._selected_single_preset().key,
            output_format=self._selected_output_format(),
            encoding=encoding,
            byte_length=byte_length,
            env_name=env_name,
            prefix=self._single("prefix").text(),
            suffix=self._single("suffix").text(),
            custom_charset=self._single("charset").text() or ASCII_SAFE_CHARSET,
        )

    def _set_batch(self, batch: GenerationBatch, output_format: str) -> None:
        self._current_batch = batch
        normalized_format = normalize_output_format(output_format)
        if normalized_format == "plain" and batch.first():
            self._current_output = batch.first().value
        elif normalized_format == "json":
            self._current_output = format_generated_json(batch.first()) if len(batch.secrets) == 1 else format_json_array(batch)
        else:
            self._current_output = format_env_block(batch.secrets)
        self._set_copy_enabled(True)
        self._refresh_output()
        self._refresh_metrics()

    def _refresh_output(self) -> None:
        if not self._current_batch:
            return
        if self.reveal_checkbox.isChecked():
            self.output_area.setPlainText(self._current_output)
            return
        masked = self._current_output
        for generated in self._current_batch.secrets:
            masked = masked.replace(generated.value, mask_secret(generated.value))
        self.output_area.setPlainText(masked)

    def _refresh_metrics(self) -> None:
        generated = self._first_generated()
        if not generated:
            self.entropy_card.set_value("-")
            self.security_card.set_value("-")
            self._set_warning(None)
            return
        self.entropy_card.set_value(f"{generated.estimated_entropy_bits} bit")
        self.security_card.set_value(generated.security_level)
        warnings = []
        for item in self._current_batch.secrets if self._current_batch else ():
            warnings.extend(item.warnings)
        self._set_warning("\n".join(dict.fromkeys(warnings)) if warnings else None)

    def _show_error(self, message: str) -> None:
        self._current_batch = None
        self._current_output = ""
        self.output_area.clear()
        self.entropy_card.set_value("-")
        self.security_card.set_value("-")
        self._set_copy_enabled(False)
        self._set_warning(message)
        self.statusBar().showMessage("Generation failed")

    def _copy_text(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        self._last_clipboard_text = text
        self.statusBar().showMessage("Copied")
        seconds = int(self.clear_delay_combo.currentData())
        QTimer.singleShot(seconds * 1000, lambda: self._clear_clipboard_if_same(text))

    def _clear_clipboard_if_same(self, copied_text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard.text() == copied_text:
            clipboard.clear()
            if self._last_clipboard_text == copied_text:
                self._last_clipboard_text = ""
            self.statusBar().showMessage("Clipboard cleared")

    def _first_generated(self) -> GeneratedSecret | None:
        return self._current_batch.first() if self._current_batch else None

    def _set_copy_enabled(self, enabled: bool) -> None:
        self.copy_value_button.setEnabled(enabled)
        self.copy_env_button.setEnabled(enabled)
        self.copy_all_button.setEnabled(enabled)
        self.clear_clipboard_button.setEnabled(True)

    def _set_warning(self, message: str | None) -> None:
        if message:
            self.warning_label.setText(message)
            self.warning_label.show()
        else:
            self.warning_label.hide()

    def _selected_single_preset(self) -> SecretPreset:
        return PRESETS[str(self._single("preset").currentData())]

    def _selected_single_encoding(self) -> str:
        return normalize_encoding(str(self._single("encoding").currentData()))

    def _selected_output_format(self) -> str:
        return normalize_output_format(str(self._single("format").currentData()))

    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        target = normalize_encoding(value)
        for index in range(combo.count()):
            if normalize_encoding(str(combo.itemData(index))) == target:
                combo.setCurrentIndex(index)
                return

    def _single(self, key: str):
        return self.single_widgets[key]
