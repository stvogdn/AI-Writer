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
from ai_writer.ui.components import PromptSelector, SettingsDialog, PromptManagerDialog, MainMenuBar, EditorToolbar


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
        self.main_menu = MainMenuBar(self, has_docx_support=self.file_manager.has_docx_support)
        self.setMenuBar(self.main_menu)

        # Connect signals
        self.main_menu.new_file_requested.connect(self._on_new_file)
        self.main_menu.open_file_requested.connect(self._on_open_file)
        self.main_menu.save_file_requested.connect(self._on_save_file)
        self.main_menu.save_as_txt_requested.connect(self._save_as_txt)
        self.main_menu.save_as_docx_requested.connect(self._save_as_docx)
        self.main_menu.exit_requested.connect(self.close)
        
        self.main_menu.spell_check_toggled.connect(self._on_spell_check_toggled)
        
        self.main_menu.general_settings_requested.connect(self._show_settings_dialog)
        self.main_menu.manage_prompts_requested.connect(self._open_prompt_manager)
        self.main_menu.about_requested.connect(self._show_about_dialog)

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
            # If we already have a file path, save to it directly
            path = self.file_manager.current_file
            if path.endswith(".docx"):
                success = self.file_manager.save_as_docx(text, file_path=path)
            else:
                success = self.file_manager.save_as_txt(text, file_path=path)
            
            if success:
                self.statusBar.showMessage(f"Saved to {path}")
        else:
            # Otherwise use default format (Save As)
            if self.file_manager.save_with_default_format(text):
                self.statusBar.showMessage(f"Saved to {self.file_manager.current_file}")

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
        self.toolbar = EditorToolbar(
            self, 
            current_theme=self.current_theme, 
            has_docx_support=self.file_manager.has_docx_support
        )
        
        # Connect toolbar signals
        self.toolbar.theme_toggled.connect(self.toggle_theme)
        self.toolbar.scan_requested.connect(self.scan_models)
        self.toolbar.model_changed.connect(self._on_text_changed)
        self.toolbar.prompt_changed.connect(self._on_prompt_changed)
        self.toolbar.generate_requested.connect(self.start_generation)
        self.toolbar.save_txt_requested.connect(self._save_as_txt)
        self.toolbar.save_docx_requested.connect(self._save_as_docx)
        
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

    def _open_prompt_manager(self):
        """Open the prompt management dialog."""
        dialog = PromptManagerDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Re-fetch prompts
            self.toolbar.get_prompt_selector().refresh_prompts()

    def _connect_signals(self):
        """Connect additional signals."""
        # Removed inner combobox connection, its handled by toolbar now.
        pass

    # Event handlers
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.setStyleSheet(DARK_THEME)
        else:
            self.current_theme = "light"
            self.setStyleSheet(LIGHT_THEME)

        self.toolbar.set_theme_icon(self.current_theme)

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
        current_model = self.toolbar.current_model()
        if current_model and current_model not in ["Select model...", "No models found"]:
            self.toolbar.get_prompt_selector().set_model_filter(current_model)

    def _on_text_changed(self):
        """Handle text editor content change."""
        text = self.editor.toPlainText()
        self.toolbar.set_character_count(len(text))

        model = self.toolbar.current_model()
        has_text = len(text.strip()) > 0
        has_model = model not in ["Select model...", "No models found"]
        self.toolbar.set_generate_enabled(has_text and has_model)

    # Ollama operations
    def scan_models(self):
        """Scan for available Ollama models."""
        self.statusBar.showMessage("Scanning for models...")
        self.toolbar.set_models([]) # Clear combo box

        self.worker = OllamaClient.scan_models()
        self.worker.models_loaded.connect(self._on_models_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_models_loaded(self, models):
        """Handle successful model loading."""
        if not models:
            self.toolbar.set_models([])
            self.statusBar.showMessage("❌ No models available")
            self.toolbar.set_generate_enabled(False)
        else:
            default_model = None
            if (
                self.settings.ollama.default_model
                and self.settings.ollama.default_model in models
            ):
                default_model = self.settings.ollama.default_model

            self.toolbar.set_models(models, default_model)
            self.statusBar.showMessage(f"✓ {len(models)} models available")

            self._on_text_changed()

    def start_generation(self):
        """Start text generation process."""
        text = self.editor.toPlainText()
        model = self.toolbar.current_model()

        if not text.strip() or model in ["Select model...", "No models found"]:
            QMessageBox.warning(
                self, "Warning", "Please enter text and select a model."
            )
            return

        self.generation_cursor_pos = len(text)

        # Prepare the prompt - use template if selected
        full_prompt = self._prepare_prompt_for_generation(text)

        self.toolbar.set_generate_enabled(False)
        self.toolbar.set_generate_text("⏳ Generating...")
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
        prompt_template = self.toolbar.get_prompt_selector().get_selected_prompt_content()
        
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
        self.toolbar.set_generate_enabled(True)
        self.toolbar.set_generate_text("✨ Generate")

    # File operations
    def _save_as_txt(self):
        """Save document as text file."""
        text = self.editor.toPlainText()
        path = self.file_manager.current_file
        if path:
            success = self.file_manager.save_as_txt(text, file_path=path)
        else:
            success = self.file_manager.save_as_txt(text)
            
        if success:
            self.statusBar.showMessage(
                f"✓ Saved to {self.file_manager.current_file_path}"
            )

    def _save_as_docx(self):
        """Save document as Word file."""
        text = self.editor.toPlainText()
        path = self.file_manager.current_file
        if path:
            success = self.file_manager.save_as_docx(text, file_path=path)
        else:
            success = self.file_manager.save_as_docx(text)
            
        if success:
            self.statusBar.showMessage(
                f"✓ Saved to {self.file_manager.current_file_path}"
            )

    def closeEvent(self, event):
        """Handle application close event."""
        # Save settings before closing
        save_settings()
        event.accept()
