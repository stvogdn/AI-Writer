"""Main window for the AI Writer application."""

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
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
from ai_writer.ui.components import PromptSelector, SettingsDialog, PromptManagerDialog


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

        # Set up menu bar
        self._setup_menubar()

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

        # Create main editor area
        editor_widget = self._create_editor_area()
        main_layout.addWidget(editor_widget)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def _setup_menubar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new document")
        new_action.triggered.connect(self._on_new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing document")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save the current document")
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)
        
        save_as_menu = file_menu.addMenu("Save &As")
        
        save_txt_action = QAction("Text File (.txt)", self)
        save_txt_action.triggered.connect(self._save_as_txt)
        save_as_menu.addAction(save_txt_action)
        
        if self.file_manager.has_docx_support:
            save_docx_action = QAction("Word Document (.docx)", self)
            save_docx_action.triggered.connect(self._save_as_docx)
            save_as_menu.addAction(save_docx_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.spell_check_action = QAction("&Spell Check", self)
        self.spell_check_action.setCheckable(True)
        if SpellChecker.is_available():
            self.spell_check_action.setChecked(self.settings.spell_check.enabled)
            self.spell_check_action.toggled.connect(self._on_spell_check_toggled)
            edit_menu.addAction(self.spell_check_action)
        else:
            self.spell_check_action.setEnabled(False)
            edit_menu.addAction(self.spell_check_action)

        # Settings Menu
        settings_menu = menubar.addMenu("&Settings")
        
        gen_settings_action = QAction("&General Settings...", self)
        gen_settings_action.setStatusTip("Configure temperature, tokens, and Ollama URL")
        gen_settings_action.triggered.connect(self._show_settings_dialog)
        settings_menu.addAction(gen_settings_action)
        
        settings_menu.addSeparator()
        
        prompts_action = QAction("&Manage Prompts...", self)
        prompts_action.triggered.connect(self._open_prompt_manager)
        settings_menu.addAction(prompts_action)
        
        settings_menu.addSeparator()
        
        about_action = QAction("&About AI-Writer", self)
        about_action.triggered.connect(self._show_about_dialog)
        settings_menu.addAction(about_action)

    def _on_new_file(self):
        """Clear document and reset state for a new file."""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, "New Document",
                "Start a new document? Any unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        self.editor.clear()
        self.file_manager.current_file = None
        self.statusBar.showMessage("New document created")

    def _on_open_file(self):
        """Open a file dialog and load the selected file."""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "All Supported (*.txt *.docx *.md);;Text Files (*.txt);;Word Documents (*.docx);;Markdown (*.md)"
        )
        
        if file_path:
            content = self.file_manager.load_file(file_path)
            if content is not None:
                self.editor.setPlainText(content)
                self.statusBar.showMessage(f"Loaded {file_path}")

    def _on_save_file(self):
        """Save the current document."""
        text = self.editor.toPlainText()
        if self.file_manager.current_file:
            # If we already have a file path, save to it
            path = self.file_manager.current_file
            if path.endswith(".docx"):
                success = self.file_manager.save_as_docx(text)
            else:
                success = self.file_manager.save_as_txt(text)
            
            if success:
                self.statusBar.showMessage(f"Saved to {path}")
        else:
            # Otherwise use default format (Save As)
            self.file_manager.save_with_default_format(text)

    def _on_spell_check_menu_toggled(self, enabled: bool):
        """Sync spell check menu toggle."""
        self._on_spell_check_toggled(enabled)

    def _show_settings_dialog(self):
        """Show the integrated settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == SettingsDialog.Accepted:
            # Refresh state if needed (though SettingsDialog saves to global settings)
            self.temperature = self.settings.generation.default_temperature
            self.token_limit = self.settings.generation.default_token_limit
            self.statusBar.showMessage("Settings updated", 3000)

    def _show_about_dialog(self):
        """Show about information."""
        QMessageBox.about(
            self, "About AI-Writer",
            "<h3>AI-Writer</h3>"
            "<p>A modern writing assistant powered by AI.</p>"
            "<p>Version 0.3.1</p>"
            "<p>Requires Ollama to be running locally.</p>"
        )

    def _show_settings_info(self):
        """Show settings info or open settings."""
        self._show_settings_dialog()

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

        # Prompt Selector in Toolbar
        toolbar.addWidget(QLabel("  Template: "))
        self.prompt_selector = PromptSelector()
        self.prompt_selector.prompt_changed.connect(self._on_prompt_changed)
        toolbar.addWidget(self.prompt_selector)

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

    def _open_prompt_manager(self):
        """Open the prompt management dialog."""
        dialog = PromptManagerDialog(self)
        if dialog.exec_() == dialog.Accepted:
            self.prompt_selector.refresh_prompts()

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
