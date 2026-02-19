"""Main menu bar component for the AI Writer application."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAction, QMenuBar, QWidget

from ai_writer.config import get_settings
from ai_writer.core.spell_checker import SpellChecker


class MainMenuBar(QMenuBar):
    """Main application menu bar."""

    # File Menu Signals
    new_file_requested = pyqtSignal()
    open_file_requested = pyqtSignal()
    save_file_requested = pyqtSignal()
    save_as_txt_requested = pyqtSignal()
    save_as_docx_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    # Edit Menu Signals
    spell_check_toggled = pyqtSignal(bool)

    # Settings Menu Signals
    general_settings_requested = pyqtSignal()
    manage_prompts_requested = pyqtSignal()
    about_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, has_docx_support: bool = False):
        """Initialize the menu bar.

        Args:
            parent: Parent widget
            has_docx_support: Whether DOCX saving is supported
        """
        super().__init__(parent)
        self.settings = get_settings()
        self.has_docx_support = has_docx_support
        self.spell_check_action: QAction | None = None
        self._setup_ui()

    def _setup_ui(self):
        """Build the menu structure."""
        # --- File Menu ---
        file_menu = self.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new document")
        new_action.triggered.connect(self.new_file_requested.emit)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing document")
        open_action.triggered.connect(self.open_file_requested.emit)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save the current document")
        save_action.triggered.connect(self.save_file_requested.emit)
        file_menu.addAction(save_action)

        save_as_menu = file_menu.addMenu("Save &As")

        save_txt_action = QAction("Text File (.txt)", self)
        save_txt_action.triggered.connect(self.save_as_txt_requested.emit)
        save_as_menu.addAction(save_txt_action)

        if self.has_docx_support:
            save_docx_action = QAction("Word Document (.docx)", self)
            save_docx_action.triggered.connect(self.save_as_docx_requested.emit)
            save_as_menu.addAction(save_docx_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.exit_requested.emit)
        file_menu.addAction(exit_action)

        # --- Edit Menu ---
        edit_menu = self.addMenu("&Edit")

        self.spell_check_action = QAction("&Spell Check", self)
        self.spell_check_action.setCheckable(True)
        if SpellChecker.is_available():
            self.spell_check_action.setChecked(self.settings.spell_check.enabled)
            self.spell_check_action.toggled.connect(self.spell_check_toggled.emit)
            edit_menu.addAction(self.spell_check_action)
        else:
            self.spell_check_action.setEnabled(False)
            edit_menu.addAction(self.spell_check_action)

        # --- Settings Menu ---
        settings_menu = self.addMenu("&Settings")

        gen_settings_action = QAction("&General Settings...", self)
        gen_settings_action.setStatusTip("Configure temperature, tokens, and Ollama URL")
        gen_settings_action.triggered.connect(self.general_settings_requested.emit)
        settings_menu.addAction(gen_settings_action)

        settings_menu.addSeparator()

        prompts_action = QAction("&Manage Prompts...", self)
        prompts_action.triggered.connect(self.manage_prompts_requested.emit)
        settings_menu.addAction(prompts_action)

        settings_menu.addSeparator()

        about_action = QAction("&About AI-Writer", self)
        about_action.triggered.connect(self.about_requested.emit)
        settings_menu.addAction(about_action)

    def set_spell_check_enabled(self, checked: bool):
        """Update the spell check toggle state programmatically."""
        if self.spell_check_action:
            # Block signals to prevent recursive emit when updating from external source
            self.spell_check_action.blockSignals(True)
            self.spell_check_action.setChecked(checked)
            self.spell_check_action.blockSignals(False)
