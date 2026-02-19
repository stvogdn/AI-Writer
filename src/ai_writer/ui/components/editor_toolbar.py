"""Toolbar component for the AI Writer application."""

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QWidget,
)

from ai_writer.ui.components import PromptSelector


class EditorToolbar(QToolBar):
    """Main application toolbar for editing and generating."""

    theme_toggled = pyqtSignal()
    scan_requested = pyqtSignal()
    model_changed = pyqtSignal()
    prompt_changed = pyqtSignal(str)
    generate_requested = pyqtSignal()
    save_txt_requested = pyqtSignal()
    save_docx_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, current_theme: str = "light", has_docx_support: bool = False):
        """Initialize the editor toolbar.

        Args:
            parent: Parent widget
            current_theme: Initial UI theme ('light' or 'dark')
            has_docx_support: Whether to show the Word save button
        """
        super().__init__(parent)
        self.current_theme = current_theme
        self.has_docx_support = has_docx_support
        
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self._setup_ui()

    def _setup_ui(self):
        """Build the toolbar widget structure."""
        # Theme toggle
        self.theme_btn = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.clicked.connect(self.theme_toggled.emit)
        self.addWidget(self.theme_btn)

        self.addSeparator()

        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(180)
        self.model_combo.addItem("Select model...")
        self.model_combo.currentTextChanged.connect(self._on_model_combo_changed)
        
        self.addWidget(QLabel("  Model: "))
        self.addWidget(self.model_combo)

        self.scan_btn = QPushButton("🔄")
        self.scan_btn.setToolTip("Refresh Models")
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        self.addWidget(self.scan_btn)

        self.addSeparator()

        # Prompt Selector in Toolbar
        self.addWidget(QLabel("  Template: "))
        self.prompt_selector = PromptSelector()
        self.prompt_selector.prompt_changed.connect(self.prompt_changed.emit)
        self.addWidget(self.prompt_selector)

        self.addSeparator()

        # Generate button
        self.generate_btn = QPushButton("✨ Generate")
        self.generate_btn.setObjectName("generate-btn")
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        self.generate_btn.setEnabled(False)
        self.addWidget(self.generate_btn)

        self.addSeparator()

        # Save buttons
        self.save_txt_btn = QPushButton("📄 Save .txt")
        self.save_txt_btn.clicked.connect(self.save_txt_requested.emit)
        self.addWidget(self.save_txt_btn)

        if self.has_docx_support:
            self.save_doc_btn = QPushButton("📕 Save .docx")
            self.save_doc_btn.clicked.connect(self.save_docx_requested.emit)
            self.addWidget(self.save_doc_btn)
        else:
            self.addWidget(QLabel("  (install python-docx for .docx)"))

        # Stretch and character count
        stretch_widget = QWidget()
        stretch_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(stretch_widget)

        self.char_label = QLabel("0 chars")
        self.addWidget(self.char_label)

    # --- Public API for state management ---

    def set_theme_icon(self, theme: str):
        """Update the theme button icon."""
        self.current_theme = theme
        self.theme_btn.setText("☀️" if theme == "dark" else "🌙")

    def set_models(self, models: list[str], default_model: str | None = None):
        """Update the available models combo box."""
        # Block signals to prevent spurious model_changed emits
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        
        if not models:
            self.model_combo.addItem("No models found")
        else:
            self.model_combo.addItems(models)
            if default_model and default_model in models:
                self.model_combo.setCurrentText(default_model)
                
        self.model_combo.blockSignals(False)

    def current_model(self) -> str:
        """Get the currently selected model."""
        return self.model_combo.currentText()

    def set_generate_enabled(self, enabled: bool):
        """Enable or disable the generate button."""
        self.generate_btn.setEnabled(enabled)

    def set_generate_text(self, text: str):
        """Update the text of the generate button."""
        self.generate_btn.setText(text)

    def set_character_count(self, count: int):
        """Update the character count label."""
        self.char_label.setText(f"{count} chars")

    def get_prompt_selector(self) -> PromptSelector:
        """Access the nested PromptSelector component."""
        return self.prompt_selector

    # --- Internal Event Handlers ---

    def _on_model_combo_changed(self, model_name: str):
        """Handle internal combobox changes and forward signal."""
        # Update nested prompt selector filter
        if model_name and model_name not in ["Select model...", "No models found"]:
            self.prompt_selector.set_model_filter(model_name)
        
        self.model_changed.emit()
