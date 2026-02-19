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
    with patch('ai_writer.ui.main_window.get_settings') as mock_settings:
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
        mock_settings.return_value.ollama.default_model = None

        with patch('ai_writer.ui.main_window.OllamaClient'):
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
        assert not main_window.generate_btn.isEnabled()

        # Default temperature should be set
        assert main_window.temperature == 0.7

        # Default token limit should be set
        assert main_window.token_limit == 140

    def test_temperature_slider_changes_value(self, main_window):
        """Test that temperature slider changes the temperature value."""

        # Simulate slider movement
        main_window.temp_slider.setValue(50)  # 0.5 temperature

        assert main_window.temperature == 0.5
        assert main_window.temp_value_label.text() == "0.50"

    def test_token_limit_spinbox_changes_value(self, main_window):
        """Test that token limit spinbox changes the token limit."""

        # Change spinbox value
        main_window.token_spinbox.setValue(200)

        assert main_window.token_limit == 200

    def test_theme_toggle(self, main_window):
        """Test theme toggling functionality."""
        initial_theme = main_window.current_theme

        # Click theme toggle button
        QTest.mouseClick(main_window.theme_btn, Qt.LeftButton)

        # Theme should have changed
        assert main_window.current_theme != initial_theme

    def test_text_change_enables_generate_button(self, main_window):
        """Test that adding text and selecting model enables generate button."""
        # Initially disabled
        assert not main_window.generate_btn.isEnabled()

        # Add a model to combo
        main_window.model_combo.clear()
        main_window.model_combo.addItem("test-model")
        main_window.model_combo.setCurrentText("test-model")

        # Add some text
        main_window.editor.setPlainText("Test text")

        # Should trigger text change handler
        main_window._on_text_changed()

        # Generate button should now be enabled
        assert main_window.generate_btn.isEnabled()

    def test_character_count_updates(self, main_window):
        """Test that character count updates when text changes."""
        test_text = "Hello, world!"
        main_window.editor.setPlainText(test_text)
        main_window._on_text_changed()

        assert main_window.char_label.text() == f"{len(test_text)} chars"

    @patch('ai_writer.ui.main_window.QMessageBox.warning')
    def test_generate_without_model_shows_warning(self, mock_warning, main_window):
        """Test that trying to generate without a model shows warning."""
        main_window.editor.setPlainText("Some text")
        main_window.model_combo.clear()
        main_window.model_combo.addItem("Select model...")
        main_window.model_combo.setCurrentText("Select model...")

        main_window.start_generation()

        mock_warning.assert_called_once()

    @patch('ai_writer.ui.main_window.QMessageBox.warning')
    def test_generate_without_text_shows_warning(self, mock_warning, main_window):
        """Test that trying to generate without text shows warning."""
        main_window.editor.setPlainText("")
        main_window.model_combo.clear()
        main_window.model_combo.addItem("test-model")
        main_window.model_combo.setCurrentText("test-model")

        main_window.start_generation()

        mock_warning.assert_called_once()


class TestMainWindowModelOperations:
    """Test Ollama model-related operations."""

    def test_models_loaded_success(self, main_window):
        """Test successful model loading."""
        models = ["model1", "model2", "model3"]
        main_window._on_models_loaded(models)

        # Check that models were added to combo
        combo_items = [main_window.model_combo.itemText(i)
                      for i in range(main_window.model_combo.count())]
        assert combo_items == models

    def test_models_loaded_empty(self, main_window):
        """Test handling of empty model list."""
        main_window._on_models_loaded([])

        assert main_window.model_combo.itemText(0) == "No models found"
        assert not main_window.generate_btn.isEnabled()

    def test_error_handling(self, main_window):
        """Test error handling."""
        with patch('ai_writer.ui.main_window.QMessageBox.critical') as mock_critical:
            main_window._on_error("Test error message")

            mock_critical.assert_called_once()
            # Generate button should be reset
            assert main_window.generate_btn.text() == "✨ Generate"
            assert main_window.generate_btn.isEnabled()


class TestMainWindowFileOperations:
    """Test file operation functionality."""

    def test_save_txt_calls_file_manager(self, main_window):
        """Test that save TXT calls file manager."""
        with patch.object(main_window.file_manager, 'save_as_txt') as mock_save:
            mock_save.return_value = True
            main_window.file_manager.current_file_path = "test.txt"

            main_window.editor.setPlainText("Test content")
            main_window._save_as_txt()

            mock_save.assert_called_once_with("Test content")

    def test_save_docx_calls_file_manager(self, main_window):
        """Test that save DOCX calls file manager."""
        with patch.object(main_window.file_manager, 'save_as_docx') as mock_save:
            mock_save.return_value = True
            main_window.file_manager.current_file_path = "test.docx"

            main_window.editor.setPlainText("Test content")
            main_window._save_as_docx()

            mock_save.assert_called_once_with("Test content")
