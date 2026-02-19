"""Test main window UI functionality."""

from unittest.mock import Mock, patch

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from ai_writer.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for testing."""
    with patch("ai_writer.ui.main_window.get_settings") as mock_settings:
        # Mock settings to avoid loading real config
        mock_settings.return_value = Mock()
        mock_settings.return_value.ui.window_width = 1000
        mock_settings.return_value.ui.window_height = 700
        mock_settings.return_value.ui.default_theme = "light"
        mock_settings.return_value.ui.sidebar_width = 280
        mock_settings.return_value.generation.default_temperature = 0.7
        mock_settings.return_value.generation.default_token_limit = 140
        mock_settings.return_value.generation.min_temperature = 0.0
        mock_settings.return_value.generation.max_temperature = 2.0
        mock_settings.return_value.generation.min_token_limit = 10
        mock_settings.return_value.generation.max_token_limit = 2000
        mock_settings.return_value.ollama.url = "http://localhost:11434"
        mock_settings.return_value.ollama.default_model = ""
        mock_settings.return_value.spell_check.enabled = False
        mock_settings.return_value.spell_check.language = "en_US"
        mock_settings.return_value.spell_check.highlight_color = "#ff0000"

        with patch("ai_writer.ui.main_window.OllamaClient"):
            window = MainWindow()
            yield window
            window.close()


class TestMainWindow:
    """Test MainWindow class."""

    def test_window_creation(self, main_window):
        """Test that main window is created successfully."""
        assert main_window.windowTitle() == "AI Writer"
        assert main_window.minimumSize().width() == 1000
        assert main_window.minimumSize().height() == 700

    def test_initial_state(self, main_window):
        """Test initial UI state."""
        # Generate button should be disabled initially
        assert not main_window.toolbar.generate_btn.isEnabled()

        # Default token limit should be set
        assert main_window.token_limit == 140


    def test_theme_toggle(self, main_window):
        """Test theme toggling functionality."""
        initial_theme = main_window.current_theme

        # Click theme toggle button
        QTest.mouseClick(main_window.toolbar.theme_btn, Qt.LeftButton)

        # Theme should have changed
        assert main_window.current_theme != initial_theme

    def test_text_change_enables_generate_button(self, main_window):
        """Test that adding text and selecting model enables generate button."""
        # Initially disabled
        assert not main_window.toolbar.generate_btn.isEnabled()

        # Add a model to combo
        main_window.toolbar.model_combo.clear()
        main_window.toolbar.model_combo.addItem("test-model")
        main_window.toolbar.model_combo.setCurrentText("test-model")

        # Add some text
        main_window.editor.setPlainText("Test text")

        # Should trigger text change handler
        main_window._on_text_changed()

        # Generate button should now be enabled
        assert main_window.toolbar.generate_btn.isEnabled()

    def test_character_count_updates(self, main_window):
        """Test that character count updates when text changes."""
        test_text = "Hello, world!"
        main_window.editor.setPlainText(test_text)
        main_window._on_text_changed()

        assert main_window.toolbar.char_label.text() == f"{len(test_text)} chars"

    @patch("ai_writer.ui.main_window.QMessageBox.warning")
    def test_generate_without_model_shows_warning(self, mock_warning, main_window):
        """Test that trying to generate without a model shows warning."""
        main_window.editor.setPlainText("Some text")
        main_window.toolbar.model_combo.clear()
        main_window.toolbar.model_combo.addItem("Select model...")
        main_window.toolbar.model_combo.setCurrentText("Select model...")

        main_window.start_generation()

        mock_warning.assert_called_once()

    @patch("ai_writer.ui.main_window.QMessageBox.warning")
    def test_generate_without_text_shows_warning(self, mock_warning, main_window):
        """Test that trying to generate without text shows warning."""
        main_window.editor.setPlainText("")
        main_window.toolbar.model_combo.clear()
        main_window.toolbar.model_combo.addItem("test-model")
        main_window.toolbar.model_combo.setCurrentText("test-model")

        main_window.start_generation()

        mock_warning.assert_called_once()


class TestMainWindowModelOperations:
    """Test Ollama model-related operations."""

    def test_models_loaded_success(self, main_window):
        """Test successful model loading."""
        models = ["model1", "model2", "model3"]
        main_window._on_models_loaded(models)

        # Check that models were added to combo
        combo_items = [
            main_window.toolbar.model_combo.itemText(i)
            for i in range(main_window.toolbar.model_combo.count())
        ]
        assert combo_items == models

    def test_models_loaded_empty(self, main_window):
        """Test handling of empty model list."""
        main_window._on_models_loaded([])

        assert main_window.toolbar.model_combo.itemText(0) == "No models found"
        assert not main_window.toolbar.generate_btn.isEnabled()

    def test_error_handling(self, main_window):
        """Test error handling."""
        with patch("ai_writer.ui.main_window.QMessageBox.critical") as mock_critical:
            main_window._on_error("Test error message")

            mock_critical.assert_called_once()
            # Generate button should be reset
            assert main_window.toolbar.generate_btn.text() == "✨ Generate"
            assert main_window.toolbar.generate_btn.isEnabled()


class TestMainWindowFileOperations:
    """Test file operation functionality."""

    def test_save_txt_calls_file_manager(self, main_window):
        """Test that save TXT calls file manager."""
        with patch.object(main_window.file_manager, "save_as_txt") as mock_save:
            mock_save.return_value = True
            main_window.file_manager.current_file = "test.txt"

            main_window.editor.setPlainText("Test content")
            main_window._save_as_txt()

            mock_save.assert_called_once_with("Test content", file_path="test.txt")

    def test_save_docx_calls_file_manager(self, main_window):
        """Test that save DOCX calls file manager."""
        with patch.object(main_window.file_manager, "save_as_docx") as mock_save:
            mock_save.return_value = True
            main_window.file_manager.current_file = "test.docx"

            main_window.editor.setPlainText("Test content")
            main_window._save_as_docx()

            mock_save.assert_called_once_with("Test content", file_path="test.docx")


class TestMainWindowMenuBar:
    """Test menu bar functionality."""

    def test_menubar_exists(self, main_window):
        """Test that the menu bar and expected menus exist."""
        menubar = main_window.menuBar()
        assert menubar is not None
        
        actions = menubar.actions()
        menu_titles = [action.text() for action in actions]
        assert "&File" in menu_titles
        assert "&Edit" in menu_titles
        assert "&Settings" in menu_titles

    def test_file_new_clears_editor(self, main_window):
        """Test that File -> New clears the editor."""
        main_window.editor.setPlainText("Some text")
        
        # Mock QMessageBox to auto-accept
        with patch("ai_writer.ui.main_window.QMessageBox.question") as mock_question:
            mock_question.return_value = 16384  # QMessageBox.Yes
            main_window._on_new_file()
            
        assert main_window.editor.toPlainText() == ""
        assert main_window.file_manager.current_file is None

    def test_file_open_calls_file_manager(self, main_window):
        """Test that File -> Open calls file manager load_file."""
        with patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
            mock_dialog.return_value = ("test.txt", "Text Files (*.txt)")
            with patch.object(main_window.file_manager, "load_file") as mock_load:
                mock_load.return_value = "Loaded content"
                main_window._on_open_file()
                
                mock_load.assert_called_once()
                assert main_window.editor.toPlainText() == "Loaded content"


    def test_about_dialog_shows(self, main_window):
        """Test that About dialog shows."""
        with patch("ai_writer.ui.main_window.QMessageBox.about") as mock_about:
            main_window._show_about_dialog()
            mock_about.assert_called_once()
