"""Main window for the AI Writer application."""

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ai_writer.config import get_settings, save_settings
from ai_writer.core import FileManager, OllamaClient, initialize_default_prompts
from ai_writer.core.spell_checker import SpellChecker
from ai_writer.ui.styles import DARK_THEME, LIGHT_THEME
from ai_writer.ui.components.prompt_selector import PromptSelector


class MainWindow(QMainWindow):
    """Main application window for AI Writer."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.settings = get_settings()
        self.file_manager = FileManager(self)
        
        # Initialize default prompts if none exist
        initialize_default_prompts()
        
        # Initialize spell checker
        self.spell_checker = None
        
        self._setup_window()
        self._init_state()
        self._setup_ui()
        self._connect_signals()
        
        # Initialize spell checker after UI is set up
        self._init_spell_checker()

        # Start model scan
        self.setWindowTitle("AI Writer")

    def _setup_window(self):
        """Set up basic window properties."""
        self.setMinimumSize(
            self.settings.ui.window_width, self.settings.ui.window_height
        )
        self.current_theme = self.settings.ui.default_theme
        self.setStyleSheet(LIGHT_THEME if self.current_theme == "light" else DARK_THEME)

    def _init_state(self):
        """Initialize application state."""
        self.temperature = self.settings.generation.default_temperature
        self.token_limit = self.settings.generation.default_token_limit
        self.generation_cursor_pos = 0

    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Create main editor area and sidebar
        editor_widget = self._create_editor_area()
        sidebar = self._create_sidebar()

        splitter.addWidget(editor_widget)
        splitter.addWidget(sidebar)
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def _create_editor_area(self) -> QWidget:
        """Create the main editor area with toolbar and text editor."""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setSpacing(0)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = self._create_toolbar()
        editor_layout.addWidget(self.toolbar)

        # Main text editor
        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setPlaceholderText(
            "Start writing your story here... "
            "Press 'Generate' to let AI continue from your cursor position."
        )
        self.editor.textChanged.connect(self._on_text_changed)
        editor_layout.addWidget(self.editor)

        return editor_widget

    def _create_toolbar(self) -> QToolBar:
        """Create the application toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))

        # Theme toggle
        self.theme_btn = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_btn)

        toolbar.addSeparator()

        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(180)
        self.model_combo.addItem("Select model...")
        toolbar.addWidget(QLabel("  Model: "))
        toolbar.addWidget(self.model_combo)

        self.scan_btn = QPushButton("🔄")
        self.scan_btn.setToolTip("Refresh Models")
        self.scan_btn.clicked.connect(self.scan_models)
        toolbar.addWidget(self.scan_btn)

        toolbar.addSeparator()

        # Generate button
        self.generate_btn = QPushButton("✨ Generate")
        self.generate_btn.setObjectName("generate-btn")
        self.generate_btn.clicked.connect(self.start_generation)
        self.generate_btn.setEnabled(False)
        toolbar.addWidget(self.generate_btn)

        toolbar.addSeparator()

        # Save buttons
        self.save_txt_btn = QPushButton("📄 Save .txt")
        self.save_txt_btn.clicked.connect(self._save_as_txt)
        toolbar.addWidget(self.save_txt_btn)

        if self.file_manager.has_docx_support:
            self.save_doc_btn = QPushButton("📕 Save .docx")
            self.save_doc_btn.clicked.connect(self._save_as_docx)
            toolbar.addWidget(self.save_doc_btn)
        else:
            toolbar.addWidget(QLabel("  (install python-docx for .docx)"))

        # Stretch and character count
        stretch_widget = QWidget()
        stretch_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(stretch_widget)

        self.char_label = QLabel("0 chars")
        toolbar.addWidget(self.char_label)

        return toolbar

    def _create_sidebar(self) -> QFrame:
        """Create the settings sidebar."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(self.settings.ui.sidebar_width)
        sidebar_layout = QVBoxLayout(sidebar)

        # Temperature control
        self._add_temperature_control(sidebar_layout)
        sidebar_layout.addSpacing(20)

        # Token limit control
        self._add_token_control(sidebar_layout)
        sidebar_layout.addSpacing(20)

        # Prompt selector
        self.prompt_selector = PromptSelector()
        self.prompt_selector.prompt_changed.connect(self._on_prompt_changed)
        sidebar_layout.addWidget(self.prompt_selector)
        sidebar_layout.addSpacing(20)

        # Ollama URL control
        self._add_ollama_url_control(sidebar_layout)
        sidebar_layout.addSpacing(20)
        
        # Spell check control (if available)
        if SpellChecker.is_available():
            self._add_spell_check_control(sidebar_layout)
            sidebar_layout.addSpacing(20)

        # Tips section
        self._add_tips_section(sidebar_layout)
        sidebar_layout.addStretch()

        return sidebar

    def _add_temperature_control(self, layout):
        """Add temperature control to sidebar."""
        temp_title = QLabel("🌡️ Temperature")
        temp_title.setObjectName("sidebar-title")
        layout.addWidget(temp_title)

        self.temp_value_label = QLabel(f"{self.temperature:.2f}")
        self.temp_value_label.setAlignment(Qt.AlignRight)
        self.temp_value_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #007aff;"
        )
        layout.addWidget(self.temp_value_label)

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(int(self.settings.generation.min_temperature * 100))
        self.temp_slider.setMaximum(int(self.settings.generation.max_temperature * 100))
        self.temp_slider.setValue(int(self.temperature * 100))
        self.temp_slider.setTickPosition(QSlider.TicksBelow)
        self.temp_slider.setTickInterval(25)
        self.temp_slider.valueChanged.connect(self._on_temperature_changed)
        layout.addWidget(self.temp_slider)

        # Temperature hints
        temp_hints = QHBoxLayout()
        temp_hints.addWidget(QLabel("🎯"))
        temp_hints.addStretch()
        temp_hints.addWidget(QLabel("⚖️"))
        temp_hints.addStretch()
        temp_hints.addWidget(QLabel("🎨"))
        layout.addLayout(temp_hints)

    def _add_token_control(self, layout):
        """Add token limit control to sidebar."""
        token_title = QLabel("📊 Token Limit")
        token_title.setObjectName("sidebar-title")
        layout.addWidget(token_title)

        self.token_spinbox = QSpinBox()
        self.token_spinbox.setMinimum(self.settings.generation.min_token_limit)
        self.token_spinbox.setMaximum(self.settings.generation.max_token_limit)
        self.token_spinbox.setValue(self.token_limit)
        self.token_spinbox.setSuffix(" tokens")
        self.token_spinbox.valueChanged.connect(self._on_token_limit_changed)
        layout.addWidget(self.token_spinbox)

        token_hints = QLabel("Higher = longer response\\nLower = shorter response")
        token_hints.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(token_hints)

    def _add_ollama_url_control(self, layout):
        """Add Ollama URL control to sidebar."""
        url_title = QLabel("🔗 Ollama URL")
        url_title.setObjectName("sidebar-title")
        layout.addWidget(url_title)

        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setText(self.settings.ollama.url)
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_url_input.editingFinished.connect(self._on_ollama_url_changed)
        layout.addWidget(self.ollama_url_input)

        url_hints = QLabel("Ollama server URL")
        url_hints.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(url_hints)
    
    def _add_spell_check_control(self, layout):
        """Add spell check control to sidebar."""
        spell_title = QLabel("📝 Spell Check")
        spell_title.setObjectName("sidebar-title")
        layout.addWidget(spell_title)
        
        # Enable/disable checkbox
        from PyQt5.QtWidgets import QCheckBox
        self.spell_check_checkbox = QCheckBox("Enable spell checking")
        self.spell_check_checkbox.setChecked(self.settings.spell_check.enabled)
        self.spell_check_checkbox.toggled.connect(self._on_spell_check_toggled)
        layout.addWidget(self.spell_check_checkbox)
        
        # Language selection
        if SpellChecker.is_available():
            from PyQt5.QtWidgets import QComboBox
            lang_layout = QHBoxLayout()
            lang_layout.addWidget(QLabel("Language:"))
            
            self.spell_lang_combo = QComboBox()
            available_langs = SpellChecker.get_available_languages()
            for lang_tag in available_langs:
                self.spell_lang_combo.addItem(lang_tag)
            
            # Set current language
            current_index = self.spell_lang_combo.findText(self.settings.spell_check.language)
            if current_index >= 0:
                self.spell_lang_combo.setCurrentIndex(current_index)
            
            self.spell_lang_combo.currentTextChanged.connect(self._on_spell_language_changed)
            lang_layout.addWidget(self.spell_lang_combo)
            layout.addLayout(lang_layout)

    def _add_tips_section(self, layout):
        """Add tips section to sidebar."""
        info_title = QLabel("ℹ️ Tips")
        info_title.setObjectName("sidebar-title")
        layout.addWidget(info_title)

        tips = [
            "• Place cursor where you want AI to continue",
            "• Lower temp = more focused",
            "• Higher temp = more creative",
            "• Save your work frequently",
        ]
        for tip in tips:
            layout.addWidget(QLabel(tip))

    def _connect_signals(self):
        """Connect additional signals."""
        # Model selection change
        self.model_combo.currentTextChanged.connect(self._on_text_changed)

    # Event handlers
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.theme_btn.setText("☀️")
            self.setStyleSheet(DARK_THEME)
        else:
            self.current_theme = "light"
            self.theme_btn.setText("🌙")
            self.setStyleSheet(LIGHT_THEME)

        # Update settings
        self.settings.ui.default_theme = self.current_theme
        save_settings()

    def _on_temperature_changed(self, value: int):
        """Handle temperature slider change."""
        self.temperature = value / 100.0
        self.temp_value_label.setText(f"{self.temperature:.2f}")
        self.settings.generation.default_temperature = self.temperature
        save_settings()

    def _on_token_limit_changed(self, value: int):
        """Handle token limit change."""
        self.token_limit = value
        self.statusBar.showMessage(f"Token limit set to {self.token_limit} tokens")
        self.settings.generation.default_token_limit = self.token_limit
        save_settings()

    def _on_ollama_url_changed(self):
        """Handle Ollama URL change."""
        new_url = self.ollama_url_input.text().strip()
        if new_url and new_url != self.settings.ollama.url:
            self.settings.ollama.url = new_url
            save_settings()
            self.statusBar.showMessage(f"Ollama URL updated to {new_url}")
    
    def _on_prompt_changed(self, prompt_content: str):
        """Handle prompt template selection change.
        
        Args:
            prompt_content: The selected prompt template content
        """
        # Update model filter in prompt selector when model changes
        current_model = self.model_combo.currentText()
        if current_model and current_model not in ["Select model...", "No models found"]:
            self.prompt_selector.set_model_filter(current_model)

    def _on_text_changed(self):
        """Handle text editor content change."""
        text = self.editor.toPlainText()
        self.char_label.setText(f"{len(text)} chars")

        model = self.model_combo.currentText()
        has_text = len(text.strip()) > 0
        has_model = model not in ["Select model...", "No models found"]
        self.generate_btn.setEnabled(has_text and has_model)
        
        # Update prompt selector model filter when model changes
        if has_model:
            self.prompt_selector.set_model_filter(model)

    # Ollama operations
    def scan_models(self):
        """Scan for available Ollama models."""
        self.statusBar.showMessage("Scanning for models...")
        self.model_combo.clear()

        self.worker = OllamaClient.scan_models()
        self.worker.models_loaded.connect(self._on_models_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_models_loaded(self, models):
        """Handle successful model loading."""
        self.model_combo.clear()
        if not models:
            self.model_combo.addItem("No models found")
            self.statusBar.showMessage("❌ No models available")
            self.generate_btn.setEnabled(False)
        else:
            self.model_combo.addItems(models)
            self.statusBar.showMessage(f"✓ {len(models)} models available")

            # Set default model if configured
            if (
                self.settings.ollama.default_model
                and self.settings.ollama.default_model in models
            ):
                index = models.index(self.settings.ollama.default_model)
                self.model_combo.setCurrentIndex(index)

            self._on_text_changed()

    def start_generation(self):
        """Start text generation process."""
        text = self.editor.toPlainText()
        model = self.model_combo.currentText()

        if not text.strip() or model in ["Select model...", "No models found"]:
            QMessageBox.warning(
                self, "Warning", "Please enter text and select a model."
            )
            return

        self.generation_cursor_pos = len(text)

        # Prepare the prompt - use template if selected
        full_prompt = self._prepare_prompt_for_generation(text)

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("⏳ Generating...")
        self.statusBar.showMessage(
            f"AI is writing (Temp: {self.temperature:.2f}, "
            f"Tokens: {self.token_limit})..."
        )

        self.worker = OllamaClient.generate_text(
            model=model,
            prompt=full_prompt,
            temperature=self.temperature,
            token_limit=self.token_limit,
            stream=True
        )
        self.worker.text_chunk_received.connect(self._on_text_chunk_received)
        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_text_chunk_received(self, chunk: str):
        """Handle real-time text chunk from generator."""
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.End)
        
        # Add space if needed for first chunk
        if self.generation_cursor_pos == len(self.editor.toPlainText()):
            text = self.editor.toPlainText()
            if text and not text[-1].isspace() and chunk and not chunk[0].isspace():
                cursor.insertText(" ")
        
        cursor.insertText(chunk)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
    
    def _prepare_prompt_for_generation(self, user_text: str) -> str:
        """Prepare the final prompt for generation.
        
        Args:
            user_text: The user's input text
            
        Returns:
            Final prompt to send to the model
        """
        # Get selected prompt template 
        prompt_template = self.prompt_selector.get_selected_prompt_content()
        
        if prompt_template and prompt_template.strip():
            # Combine template with user text
            return f"{prompt_template}\n\n{user_text}"
        else:
            # No template selected, use text directly
            return user_text
        
    def _init_spell_checker(self):
        """Initialize the spell checker for the text editor."""
        if SpellChecker.is_available() and self.settings.spell_check.enabled:
            self.spell_checker = SpellChecker(self.editor)
            self.spell_checker.set_enabled(self.settings.spell_check.enabled)
            self.spell_checker.set_dictionary(self.settings.spell_check.language)
            
            # Set highlight color from settings
            from PyQt5.QtGui import QColor
            color = QColor(self.settings.spell_check.highlight_color)
            self.spell_checker.set_highlight_color(color)
    
    def _on_spell_check_toggled(self, enabled: bool):
        """Handle spell check enable/disable toggle."""
        self.settings.spell_check.enabled = enabled
        save_settings()
        
        if self.spell_checker:
            self.spell_checker.set_enabled(enabled)
        elif enabled and SpellChecker.is_available():
            # Initialize spell checker if it wasn't created before
            self._init_spell_checker()
    
    def _on_spell_language_changed(self, language: str):
        """Handle spell check language change."""
        self.settings.spell_check.language = language
        save_settings()
        
        if self.spell_checker:
            self.spell_checker.set_dictionary(language)

    def _on_generation_finished(self, completion: str):
        """Handle completion of text generation."""
        self.statusBar.showMessage(
            f"✓ Generation complete (Temp: {self.temperature:.2f}, "
            f"Tokens: {self.token_limit})"
        )
        self._reset_generate_button()
        self._on_text_changed()

    def _on_error(self, error_msg: str):
        """Handle error during Ollama operations."""
        self.statusBar.showMessage("❌ Error")
        self._reset_generate_button()
        QMessageBox.critical(self, "Error", error_msg)

    def _reset_generate_button(self):
        """Reset generate button to normal state."""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("✨ Generate")

    # File operations
    def _save_as_txt(self):
        """Save document as text file."""
        text = self.editor.toPlainText()
        if self.file_manager.save_as_txt(text):
            self.statusBar.showMessage(
                f"✓ Saved to {self.file_manager.current_file_path}"
            )

    def _save_as_docx(self):
        """Save document as Word file."""
        text = self.editor.toPlainText()
        if self.file_manager.save_as_docx(text):
            self.statusBar.showMessage(
                f"✓ Saved to {self.file_manager.current_file_path}"
            )

    def closeEvent(self, event):
        """Handle application close event."""
        # Save settings before closing
        save_settings()
        event.accept()
