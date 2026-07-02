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
    QVBoxLayout,
    QWidget,
)

from app.core.entropy import (
    calculate_byte_entropy,
    calculate_charset_entropy,
    get_entropy_warning,
    get_security_level,
)
from app.core.formatters import format_env, format_json, format_plain
from app.core.generator import ASCII_SAFE_CHARSET, generate_secret
from app.core.presets import PRESETS, SecretPreset
from app.core.validators import (
    normalize_charset,
    normalize_encoding,
    normalize_output_format,
    validate_env_name,
)
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
    ("plain", "Plain text"),
    ("env", ".env"),
    ("json", "JSON"),
]

DEFAULT_CUSTOM_CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
UUID_WARNING = (
    "UUID values are useful as public identifiers. They are not recommended as "
    "high-security secret keys."
)
CLIPBOARD_WARNING = (
    "Clipboard is not secure storage. Copied secrets can be read by other applications."
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SecretKeyRandomizer")
        self.resize(980, 720)
        self._last_output = ""

        self.preset_combo = QComboBox()
        for preset in PRESETS.values():
            self.preset_combo.addItem(preset.name, preset.key)

        self.encoding_combo = QComboBox()
        for value, label in ENCODINGS:
            self.encoding_combo.addItem(label, value)

        self.length_input = QSpinBox()
        self.length_input.setRange(1, 4096)
        self.length_input.setValue(32)

        self.prefix_input = QLineEdit()
        self.suffix_input = QLineEdit()
        self.env_name_input = QLineEdit()
        self.custom_charset_input = QLineEdit(DEFAULT_CUSTOM_CHARSET)

        self.output_format_combo = QComboBox()
        for value, label in OUTPUT_FORMATS:
            self.output_format_combo.addItem(label, value)
        self.output_format_combo.setCurrentIndex(1)

        self.generate_button = QPushButton("Generate")
        self.copy_button = QPushButton("Copy")
        self.copy_button.setEnabled(False)

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(170)

        self.entropy_card = MetricCard("Entropy", "-")
        self.security_card = MetricCard("Security Level", "-")

        self.warning_label = QLabel("")
        self.warning_label.setObjectName("Warning")
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()

        self.clipboard_warning_label = QLabel(CLIPBOARD_WARNING)
        self.clipboard_warning_label.setObjectName("ClipboardWarning")
        self.clipboard_warning_label.setWordWrap(True)

        self.clear_clipboard_checkbox = QCheckBox("Clear clipboard after 30 seconds")
        self.clear_clipboard_checkbox.setChecked(True)

        self._build_layout()
        self._connect_signals()
        self.apply_preset()

    def _build_layout(self) -> None:
        root = QWidget()
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(22, 18, 22, 16)
        main_layout.setSpacing(16)

        title = QLabel("SecretKeyRandomizer")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Generate high-entropy secrets with cryptographically secure randomness. "
            "Security does not rely on hidden algorithms or closed source code."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        content_layout = QGridLayout()
        content_layout.setHorizontalSpacing(16)
        content_layout.setVerticalSpacing(16)

        settings_card = self._card()
        settings_form = QFormLayout(settings_card)
        settings_form.setContentsMargins(16, 14, 16, 14)
        settings_form.setSpacing(10)
        settings_form.addRow("Preset", self.preset_combo)
        settings_form.addRow("Encoding", self.encoding_combo)
        settings_form.addRow("Bytes / chars", self.length_input)
        settings_form.addRow("Prefix", self.prefix_input)
        settings_form.addRow("Suffix", self.suffix_input)
        settings_form.addRow("ENV name", self.env_name_input)
        settings_form.addRow("Custom charset", self.custom_charset_input)
        settings_form.addRow("Output format", self.output_format_combo)

        output_card = self._card()
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(16, 14, 16, 14)
        output_layout.setSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addStretch(1)
        output_layout.addLayout(button_layout)
        output_layout.addWidget(self.output_area)
        output_layout.addWidget(self.clear_clipboard_checkbox)
        output_layout.addWidget(self.clipboard_warning_label)

        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.entropy_card)
        metrics_layout.addWidget(self.security_card)
        output_layout.addLayout(metrics_layout)
        output_layout.addWidget(self.warning_label)

        content_layout.addWidget(settings_card, 0, 0)
        content_layout.addWidget(output_card, 0, 1)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)

        main_layout.addLayout(content_layout)
        main_layout.addStretch(1)

        self.setCentralWidget(root)
        self.statusBar().showMessage("Ready")

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _connect_signals(self) -> None:
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        self.encoding_combo.currentIndexChanged.connect(self.sync_encoding_controls)
        self.generate_button.clicked.connect(self.generate)
        self.copy_button.clicked.connect(self.copy_output)

    def apply_preset(self, _index: int | None = None) -> None:
        preset = self._selected_preset()
        self.env_name_input.setText(preset.env_name)
        self.length_input.setValue(preset.byte_length)
        self.prefix_input.setText(preset.prefix)
        self.suffix_input.setText(preset.suffix)
        self._set_combo_value(self.encoding_combo, preset.encoding)
        self.sync_encoding_controls()
        self._set_warning(preset.warning)

    def sync_encoding_controls(self) -> None:
        encoding = self._selected_encoding()
        self.custom_charset_input.setEnabled(encoding == "custom-charset")
        if encoding == "uuid-v4":
            self.length_input.setEnabled(False)
            self._set_warning(UUID_WARNING)
        else:
            self.length_input.setEnabled(True)
            preset_warning = self._selected_preset().warning
            self._set_warning(preset_warning)

    def generate(self) -> None:
        try:
            preset = self._selected_preset()
            encoding = self._selected_encoding()
            output_format = self._selected_output_format()
            byte_length = int(self.length_input.value())
            prefix = self.prefix_input.text()
            suffix = self.suffix_input.text()
            env_name = self.env_name_input.text().strip()
            custom_charset = self.custom_charset_input.text()

            if output_format in {"env", "json"}:
                validate_env_name(env_name)

            secret = generate_secret(
                byte_length=byte_length,
                encoding=encoding,
                prefix=prefix,
                suffix=suffix,
                custom_charset=custom_charset,
                output_length=byte_length,
            )
            entropy_bits = self._estimate_entropy(encoding, byte_length, custom_charset)
            security_level = get_security_level(entropy_bits)
            metadata = {
                "encoding": encoding,
                "bytes": None if encoding in {"ascii-safe", "custom-charset", "uuid-v4"} else byte_length,
                "length": byte_length if encoding in {"ascii-safe", "custom-charset"} else None,
                "estimated_entropy_bits": self._display_entropy_number(entropy_bits),
                "security_level": security_level,
            }

            if output_format == "plain":
                formatted = format_plain(secret)
            elif output_format == "env":
                formatted = format_env(env_name, secret)
            else:
                formatted = format_json(env_name, secret, metadata)

            self._last_output = formatted
            self.output_area.setPlainText(formatted)
            self.copy_button.setEnabled(True)
            self.entropy_card.set_value(f"{self._display_entropy_number(entropy_bits)} bit")
            self.security_card.set_value(security_level)
            self._set_warning(self._combined_warning(preset.warning, encoding, entropy_bits))
            self.statusBar().showMessage("Generated")
        except Exception as exc:
            self._last_output = ""
            self.copy_button.setEnabled(False)
            self.output_area.clear()
            self.entropy_card.set_value("-")
            self.security_card.set_value("-")
            self._set_warning(str(exc))
            self.statusBar().showMessage("Generation failed")

    def copy_output(self) -> None:
        if not self._last_output:
            return
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._last_output)
        self.statusBar().showMessage("Copied")
        self._set_warning(CLIPBOARD_WARNING)
        if self.clear_clipboard_checkbox.isChecked():
            copied_text = self._last_output
            QTimer.singleShot(30000, lambda: self._clear_clipboard_if_same(copied_text))

    def _clear_clipboard_if_same(self, copied_text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard.text() == copied_text:
            clipboard.clear()
            self.statusBar().showMessage("Clipboard cleared")

    def _selected_preset(self) -> SecretPreset:
        key = self.preset_combo.currentData()
        return PRESETS[str(key)]

    def _selected_encoding(self) -> str:
        return normalize_encoding(str(self.encoding_combo.currentData()))

    def _selected_output_format(self) -> str:
        return normalize_output_format(str(self.output_format_combo.currentData()))

    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        target = normalize_encoding(value)
        for index in range(combo.count()):
            if normalize_encoding(str(combo.itemData(index))) == target:
                combo.setCurrentIndex(index)
                return

    def _estimate_entropy(self, encoding: str, byte_length: int, custom_charset: str) -> float:
        if encoding == "custom-charset":
            charset_size = len(normalize_charset(custom_charset))
            return calculate_charset_entropy(byte_length, charset_size)
        if encoding == "ascii-safe":
            return calculate_charset_entropy(byte_length, len(ASCII_SAFE_CHARSET))
        if encoding == "uuid-v4":
            return 122.0
        return float(calculate_byte_entropy(byte_length))

    def _combined_warning(
        self,
        preset_warning: str | None,
        encoding: str,
        entropy_bits: float,
    ) -> str | None:
        warnings = []
        if preset_warning:
            warnings.append(preset_warning)
        if encoding == "uuid-v4":
            warnings.append(UUID_WARNING)
        entropy_warning = get_entropy_warning(entropy_bits)
        if entropy_warning:
            warnings.append(entropy_warning)
        return "\n".join(warnings) if warnings else None

    def _set_warning(self, message: str | None) -> None:
        if message:
            self.warning_label.setText(message)
            self.warning_label.show()
        else:
            self.warning_label.hide()

    def _display_entropy_number(self, entropy_bits: float) -> int | float:
        if float(entropy_bits).is_integer():
            return int(entropy_bits)
        return round(entropy_bits, 2)
