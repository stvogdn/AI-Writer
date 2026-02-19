"""Settings dialog for AI Writer."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from ai_writer.config import get_settings, save_settings


class SettingsDialog(QDialog):
    """Dialog for editing application settings."""

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.settings = get_settings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Temperature
        layout.addWidget(QLabel("🌡️ Temperature"))
        temp_layout = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(int(self.settings.generation.min_temperature * 100))
        self.temp_slider.setMaximum(int(self.settings.generation.max_temperature * 100))
        self.temp_slider.setTickPosition(QSlider.TicksBelow)
        self.temp_slider.setTickInterval(25)
        temp_layout.addWidget(self.temp_slider)
        
        self.temp_label = QLabel("0.70")
        self.temp_label.setFixedWidth(40)
        temp_layout.addWidget(self.temp_label)
        layout.addLayout(temp_layout)
        
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label.setText(f"{v / 100:.2f}")
        )

        layout.addSpacing(15)

        # Token Limit
        layout.addWidget(QLabel("📊 Token Limit"))
        self.token_spinbox = QSpinBox()
        self.token_spinbox.setMinimum(self.settings.generation.min_token_limit)
        self.token_spinbox.setMaximum(self.settings.generation.max_token_limit)
        self.token_spinbox.setSuffix(" tokens")
        layout.addWidget(self.token_spinbox)

        layout.addSpacing(15)

        # Ollama URL
        layout.addWidget(QLabel("🔗 Ollama URL"))
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        layout.addWidget(self.ollama_url_input)

        layout.addStretch()
        layout.addSpacing(20)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _load_settings(self):
        """Load current settings into UI components."""
        self.temp_slider.setValue(int(self.settings.generation.default_temperature * 100))
        self.temp_label.setText(f"{self.settings.generation.default_temperature:.2f}")
        self.token_spinbox.setValue(self.settings.generation.default_token_limit)
        self.ollama_url_input.setText(self.settings.ollama.url)

    def accept(self):
        """Save settings and close dialog."""
        self.settings.generation.default_temperature = self.temp_slider.value() / 100.0
        self.settings.generation.default_token_limit = self.token_spinbox.value()
        self.settings.ollama.url = self.ollama_url_input.text().strip()
        save_settings()
        super().accept()
