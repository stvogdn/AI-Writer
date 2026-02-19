"""Test file management functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_writer.core.file_manager import FileManager


class TestFileManager:
    """Test FileManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        self.test_text = "This is a test document.\\nWith multiple lines."

    def test_init_without_parent(self):
        """Test initialization without parent widget."""
        fm = FileManager()
        assert fm.parent is None
        assert fm.current_file is None

    def test_init_with_parent(self):
        """Test initialization with parent widget."""
        parent_mock = Mock()
        fm = FileManager(parent_mock)
        assert fm.parent is parent_mock

    def test_has_docx_support(self):
        """Test DOCX support detection."""
        # Should return True if python-docx is available
        assert isinstance(self.file_manager.has_docx_support, bool)

    @patch('ai_writer.core.file_manager.QFileDialog.getSaveFileName')
    def test_save_as_txt_success(self, mock_get_save_filename):
        """Test successful TXT file saving."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            mock_get_save_filename.return_value = (f.name, "")

            try:
                result = self.file_manager.save_as_txt(self.test_text)
                assert result is True
                assert self.file_manager.current_file == f.name

                # Verify file content
                with open(f.name, encoding='utf-8') as file:
                    content = file.read()
                    assert content == self.test_text
            finally:
                Path(f.name).unlink(missing_ok=True)

    @patch('ai_writer.core.file_manager.QFileDialog.getSaveFileName')
    def test_save_as_txt_cancelled(self, mock_get_save_filename):
        """Test cancelled TXT file saving."""
        mock_get_save_filename.return_value = ("", "")  # Cancelled dialog

        result = self.file_manager.save_as_txt(self.test_text)
        assert result is False
        assert self.file_manager.current_file is None

    def test_save_as_txt_empty_text(self):
        """Test saving empty text."""
        result = self.file_manager.save_as_txt("")
        assert result is False

    def test_load_txt_file(self):
        """Test loading TXT file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_text)
            f.flush()

            try:
                content = self.file_manager.load_file(f.name)
                assert content == self.test_text
                assert self.file_manager.current_file == f.name
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        content = self.file_manager.load_file("nonexistent.txt")
        assert content is None

    def test_current_file_path_property(self):
        """Test current_file_path property."""
        assert self.file_manager.current_file_path is None

        self.file_manager.current_file = "/path/to/file.txt"
        assert self.file_manager.current_file_path == "/path/to/file.txt"


@pytest.mark.skipif(
    not hasattr(FileManager(), 'has_docx_support') or not FileManager().has_docx_support,
    reason="python-docx not available"
)
class TestFileManagerDocx:
    """Test DOCX functionality when available."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        self.test_text = "This is a test document.\\nWith multiple lines."

    @patch('ai_writer.core.file_manager.QFileDialog.getSaveFileName')
    def test_save_as_docx_success(self, mock_get_save_filename):
        """Test successful DOCX file saving."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            mock_get_save_filename.return_value = (f.name, "")

            try:
                result = self.file_manager.save_as_docx(self.test_text)
                assert result is True
                assert self.file_manager.current_file == f.name
                assert Path(f.name).exists()
            finally:
                Path(f.name).unlink(missing_ok=True)
